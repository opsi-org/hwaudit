#
# This script requires opsi >= 4.0
#

import argparse

from OPSI.Backend.JSONRPC import JSONRPCBackend
from OPSI.Logger import Logger, LOG_ERROR, LOG_DEBUG2

__version__ = "4.2.0.1"

logger = Logger()

def main(argv):
	if os.path.exists("/var/log/opsi"):
		logDir = os.path.join('/var/log/opsi')
	else:
		logDir = os.path.join('/var/log')

	logFile = os.path.join(logDir, 'hwaudit.log')

	parser = argparse.ArgumentParser(
		description="Perform hardware audit on a client and sent the result to an opsi server.",
		add_help=False
	)
	parser.add_argument('--help', action="store_true", help="Display help.")
	parser.add_argument('--version', action='version', version=__version__)
	parser.add_argument(
		'--log-level', '--loglevel', '-l', default=LOG_ERROR,
		dest="logLevel", type=int, choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
		help="Set the desired loglevel."
	)
	parser.add_argument('--log-file', '-f', dest="logFile", default=logFile, help="Path to file where debug logs will be written.")
	parser.add_argument('--hostid', '-h', help="Hostid that will be used. If nothing is set the value from --username will be used.")
	parser.add_argument('--username', '-u', help="Username to connect to the service. If nothing is set the value from --hostid will be used.")
	parser.add_argument('--password', '-p', required=True, help="Password for authentication")
	parser.add_argument('--address', '-a', required=True, help="Address to connect to. Example: https://server.domain.local:4447")

	opts = parser.parse_args()

	if opts.help:
		parser.print_help()
		sys.exit(0)

	password = opts.password

	logger.addConfidentialString(password)
	logger.setConsoleLevel(opts.logLevel)
	logger.setLogFile(opts.logFile)
	logger.setFileLevel(LOG_DEBUG2)

	logger.notice("starting hardware audit (script version {})", __version__)

	address = opts.address
	if address.startswith(u"https://"):
		address = address + u"/rpc"

	if not address:
		logger.critical(u"Address not set")
		raise RuntimeError("Address not set")

	host_id = opts.hostid or opts.username
	username = opts.username or opts.hostid

	if not (username and host_id):
		raise RuntimeError("Host id and username not set")

	logger.notice(u"Connecting to service at '{}' as '{}'", address, username)

	backendConfig = dict(
		username=username,
		password=password,
		address=address,
		application='opsi hwaudit %s' % __version__
	)

	with JSONRPCBackend(**backendConfig) as backend:
		logger.notice(u"Connected to opsi server")

		# Do hardware inventory
		logger.notice(u"Fetching opsi hw audit configuration")
		config = backend.auditHardware_getConfig()

		logger.notice(u"Running hardware inventory")
		auditHardwareOnHosts = auditHardware(config = config, hostId = username)

		logger.notice(u"Marking hardware information as obsolete")
		backend.auditHardwareOnHost_setObsolete(username)

		logger.notice(u"Sending hardware information to service")
		backend.auditHardwareOnHost_createObjects(auditHardwareOnHosts)


if __name__ == "__main__":
	logger.setConsoleLevel(LOG_ERROR)
	try:
		main(sys.argv[1:])
	except Exception as error:
		logger.logException(error)
		sys.exit(1)


logger.notice(u"Initiating reboot")
reboot()
