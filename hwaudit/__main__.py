import sys
import os
import argparse
import re

from opsicommon.logging import logger, secret_filter, init_logging
from opsicommon.logging.constants import DEFAULT_COLORED_FORMAT, LOG_ERROR, TRACE
from opsicommon.client.opsiservice import ServiceClient
from opsicommon.objects import to_json


from hwaudit import __version__

def init_audit(logFile: str) -> tuple[str, ServiceClient]:
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
		'--log-level', '--loglevel', '-l', default=LOG_ERROR,
		dest="logLevel", type=int, choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
		help="Set the desired loglevel."
	)
	parser.add_argument('--log-file', '-f', dest="logFile", default=logFile, help="Path to file where debug logs will be written.")
	parser.add_argument('--hostid', '-h', help="Hostid that will be used. If nothing is set the value from --username will be used.")
	parser.add_argument('--username', '-u', help="Username to connect to the service. If nothing is set the value from --hostid will be used.")
	# Having required=True breaks --help as it exits with exitcode 1
	parser.add_argument('--password', '-p', help="Password for authentication")
	parser.add_argument('--address', '-a', help="Address to connect to. Example: https://server.domain.local:4447")

	opts = parser.parse_args()

	if opts.help:
		parser.print_help()
		sys.exit(0)

	password = opts.password

	secret_filter.add_secrets(password)
	logFile = os.path.expanduser(re.sub("""['"]""", "", opts.logFile))

	init_logging(
		stderr_format=DEFAULT_COLORED_FORMAT,
		stderr_level=opts.logLevel,
		file_level=opts.logLevel,
		log_file=logFile
	)

	logger.notice("starting hardware audit (script version %s)", __version__)

	address = re.sub("""['"]""", "", opts.address)

	if address.startswith("https://"):
		address = address + "/rpc"

	if not address:
		logger.critical("Address not set")
		raise RuntimeError("Address not set")

	host_id = opts.hostid or opts.username
	username = opts.username or opts.hostid

	if not (username and host_id):
		raise RuntimeError("Host id and username not set")

	username = re.sub("""['"]""", "", username)
	password = re.sub("""['"]""", "", password)
	host_id = re.sub("""['"]""", "", host_id)

	service_client = ServiceClient(
		address=address,
		username=username,
		password=password,
		verify="accept_all",
		user_agent=f"opsi hwaudit {__version__}",
		jsonrpc_create_methods=True,
		jsonrpc_create_objects=True
	)

	return host_id, service_client


def main():
	"""
	Main method for hwaudit.

	This method controls the execution flow. Depending on the
	architecture/platform, different methods are important and called
	to perform the Hardware Audit.
	"""
	RUNS_ON_WINDOWS = sys.platform in ('nt', 'win32')
	if RUNS_ON_WINDOWS:
		from .hwaudit_windows import get_hwaudit
		if os.path.exists(r'C:\opsi.org\log'):
			log_dir = r'C:\opsi.org\log'
		else:
			log_dir = r'C:\opsi.org\tmp'
	else:
		from .hwaudit_posix import get_hwaudit
		if os.path.exists("/var/log/opsi"):
			log_dir = '/var/log/opsi'
		else:
			log_dir = '/var/log'
	log_file = os.path.join(log_dir, 'hwaudit.log')

	host_id, service_client = init_audit(log_file)
	logger.notice("Connecting to service at '%s' as '%s'", service_client.base_url, service_client.username)
	with service_client.connection():
		try:
			logger.notice("Fetching opsi hw audit configuration")
			config = service_client.auditHardware_getConfig()

			logger.notice("Running hardware inventory")
			audit_hardware_on_hosts = get_hwaudit(config=config, host_id=host_id)

			logger.notice("Marking hardware information as obsolete")
			service_client.auditHardwareOnHost_setObsolete(host_id)

			logger.notice("Sending hardware information to service")
			if logger.isEnabledFor(TRACE):
				logger.trace(to_json(audit_hardware_on_hosts))
			service_client.auditHardwareOnHost_createObjects(audit_hardware_on_hosts)
		except Exception as err:
			logger.error(err, exc_info=True)
	logger.notice("Exiting...")

if __name__ == "__main__":
	main()
