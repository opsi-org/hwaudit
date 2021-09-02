from typing import Dict

from OPSI.System import auditHardware
from OPSI.Backend.JSONRPC import JSONRPCBackend
from opsicommon.logging import logger

from hwaudit import __version__
#from hwaudit.opsihwauditconf import OPSI_HARDWARE_CLASSES

def makehwaudit(backendConfig: Dict[str, str]) -> None:
	"""
	Hardware Audit for Posix.

	This method calls auditHardware from the OPSI.System Posix part
	and reports the results to the RPC backend.

	:param backendConfig: Dictionary containing the configuration of the backend.
	:type backendConfig: dict
	"""
	try:
		with JSONRPCBackend(**backendConfig) as backend:
			logger.notice("Connected to opsi server")

			# Do hardware inventory
			logger.notice("Fetching opsi hw audit configuration")
			config = backend.auditHardware_getConfig()
			#config = OPSI_HARDWARE_CLASSES

			logger.notice("Running hardware inventory")
			auditHardwareOnHosts = auditHardware(config = config, hostId = backendConfig.get('host_id'))

			logger.notice("Marking hardware information as obsolete")
			backend.auditHardwareOnHost_setObsolete(backendConfig.get('host_id'))

			logger.notice("Sending hardware information to service")
			backend.auditHardwareOnHost_createObjects(auditHardwareOnHosts)
	except ValueError as error:
		logger.error("ValueError occured in makehwaudit %s:", error)
