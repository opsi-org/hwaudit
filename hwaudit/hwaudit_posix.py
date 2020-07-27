from typing import Dict

from OPSI.System import auditHardware
from OPSI.Backend.JSONRPC import JSONRPCBackend
from opsicommon.logging import logger

from . import __version__

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
			logger.notice(u"Connected to opsi server")

			# Do hardware inventory
			logger.notice(u"Fetching opsi hw audit configuration")
			config = backend.auditHardware_getConfig()

			logger.notice(u"Running hardware inventory")
			auditHardwareOnHosts = auditHardware(config = config, hostId = backendConfig.get('host_id'))

			logger.notice(u"Marking hardware information as obsolete")
			backend.auditHardwareOnHost_setObsolete(backendConfig.get('host_id'))

			logger.notice(u"Sending hardware information to service")
			backend.auditHardwareOnHost_createObjects(auditHardwareOnHosts)
	except ValueError as error:
		logger.error(u"ValueError occured in makehwaudit %s:", error)
