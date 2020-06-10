from OPSI.System import auditHardware
from OPSI.Backend.JSONRPC import JSONRPCBackend

from . import __version__

from OPSI.Logger import Logger
logger = Logger()

def makehwaudit(backendConfig):
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
		logger.error(u"ValueError occured in makehwaudit %s", error)
