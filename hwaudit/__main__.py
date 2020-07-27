import sys
import os
import argparse
from typing import Dict

from OPSI.Backend.JSONRPC import JSONRPCBackend
import opsicommon.logging
from opsicommon.logging import logger

from . import __version__

def initAudit(logFile: str) -> Dict[str, str]:
	"""
	Initialize hardware audit.

	This method parses command line arguments and extracts username, password,
	host id, address and logfile. Results are wrapped in a dictionary and
	returned. If --help or --version are specified, it reacts accordingly.

	:param logFile: Default logfile that is used if nothing is specified in args.
	:type logFile: str

	:returns: Dictionary containing the configuration for the backend access.
	"""
	parser = argparse.ArgumentParser(
		description="Perform hardware audit on a client and sent the result to an opsi server.",
		add_help=False
	)
	parser.add_argument('--help', action="store_true", help="Display help.")
	parser.add_argument('--version', action='version', version=__version__)
	parser.add_argument(
		'--log-level', '--loglevel', '-l', default=opsicommon.logging.LOG_ERROR,
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
	opsicommon.logging.init_logging(stderr_level=opts.logLevel,
									file_level=opts.logLevel,
									log_file=opts.logFile
	)

	logger.notice("starting hardware audit (script version %s)", __version__)

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

	logger.notice(u"Connecting to service at '%s' as '%s'", address, username)

	backendConfig = dict(
		username=username,
		password=password,
		address=address,
		application='opsi hwaudit %s' % __version__,
		host_id=host_id						# introduced
	)
	return backendConfig

def main():
	"""
	Main method for hwaudit.

	This method controls the execution flow. Depending on the
	architecture/platform, different methods are important and called
	to perform the Hardware Audit.
	"""
	RUNS_ON_WINDOWS = sys.platform in ('nt', 'win32')
	if RUNS_ON_WINDOWS:
		from .hwaudit_windows import makehwaudit
		if os.path.exists('C:\opsi.org\log'):
			log_dir = 'C:\opsi.org\log'
		else:
			log_dir = 'C:\opsi.org\tmp'
	else:
		from .hwaudit_posix import makehwaudit
		if os.path.exists("/var/log/opsi"):
			log_dir = '/var/log/opsi'
		else:
			log_dir = '/var/log'
	log_file = os.path.join(log_dir, 'hwaudit.log')

	backendConfig = initAudit(log_file)
	makehwaudit(backendConfig)
	logger.notice(u"Exiting...")

if __name__ == "__main__":
	main()