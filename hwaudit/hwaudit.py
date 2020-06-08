# -*- coding: utf-8 -*-

import argparse
import os
import re
import sys

if os.name == "nt":
	import wmi

from OPSI.Backend.JSONRPC import JSONRPCBackend
from OPSI.Util import objectToBeautifiedText
from OPSI.Object import AuditHardwareOnHost
from OPSI.Types import (
	forceHardwareDeviceId, forceHardwareVendorId, forceInt, forceList,
	forceUnicode, forceUnicodeList)
from OPSI.Logger import Logger, LOG_ERROR, LOG_DEBUG2

from .windows_values import VALUE_MAPPING
__version__ = "4.2.0.2"

logger = Logger()


def getHardwareInformationFromWMI(conf):
	wmiObj = wmi.WMI()

	opsiValues = {}

	for oneClass in conf:
		if not oneClass.get('Class') or not oneClass['Class'].get('Opsi') or not oneClass['Class'].get('WMI'):
			continue

		opsiName = oneClass['Class']['Opsi']
		wmiQuery = oneClass['Class']['WMI']
		mapClass = ''

		mapSep = '&'
		temp = wmiQuery.split(mapSep)
		if len(temp) == 2:
			wmiQuery, mapClass = temp

		logger.info(u"Querying: %s" % wmiQuery)
		objects = []
		try:
			objects = wmiObj.query(wmiQuery)
		except Exception as error:
			logger.error(u"Query failed: %s" % error)
			continue

		# first element? make new array for multiple devices
		if opsiName not in opsiValues:
			opsiValues[opsiName] = []

		for obj in objects:
			wmiClass = obj.ole_object.GetObjectText_().split()[2]

			obj2 = None
			if mapClass:
				assoc = obj.associators(mapClass)
				if len(assoc) > 0:
					obj2 = assoc[0]

			opsiValues[opsiName].append({})
			for item in oneClass['Values']:
				v = None
				if item.get('WMI'):
					for a in item['WMI'].split('||'):
						a = a.strip()
						c = wmiClass

						if '::' in a:
							(c, a) = a.split('::', 1)

						meth = None
						if '.' in a:
							(a, meth) = a.split('.', 1)

						op = None
						match = re.search('^(\w+)([\*\/\+\-\%]\d.*)$', a)
						if match:
							a = match.group(1)
							op = match.group(2)

						if c == wmiClass and hasattr(obj, a):
							v = getattr(obj, a)
						elif obj2 and hasattr(obj2, a):
							v = getattr(obj2, a)
						else:
							try:
								if obj2:
									logger.warning(u"%s.%s: failed to get attribute '%s' from objects %s" % (opsiName, item['Opsi'], a, [obj.__repr__(), obj2.__repr__()]))
								else:
									logger.warning(u"%s.%s: failed to get attribute '%s' from object '%s'" % (opsiName, item['Opsi'], a, obj.__repr__()))
							except Exception as error:
								logger.error(error)

							continue

						if isinstance(v, tuple) and len(v) == 1:
							v = v[0]

						if meth and v is not None:
							try:
								v = eval('v.%s' % meth)
							except Exception as evalError:
								logger.debug("Method {0!r} on function value {1!r} failed: {2!r}", meth, v, evalError)
								logger.warning(u"Method '{0}' failed on value '{1}'", meth, v)

						if op and v is not None:
							try:
								v = eval('v%s' % op)
							except Exception as evalError:
								logger.debug("Operation {0!r} on function value {1!r} failed: {2!r}", op, v, evalError)
								logger.warning(u"Operation '{0}' failed on value '{1}'", op, v)

						if item['Opsi'] in ('vendorId', 'subsystemVendorId'):
							try:
								v = forceHardwareVendorId(v)
							except Exception as hwVendError:
								logger.debug("Forcing hardware vendor id on {!r} failed: {}", v, hwVendError)
								v = None
						elif item['Opsi'] in ('deviceId', 'subsystemDeviceId'):
							try:
								v = forceHardwareDeviceId(v)
							except Exception as hwDevError:
								logger.debug("Forcing hardware device id on {!r} failed: {}", v, hwDevError)
								v = None

						if v is None:
							continue

						if isinstance(v, str):
							v = forceUnicode(v.strip())
						#if isinstance(v, bytes):
						#	v = v.strip()

						valueMappingKey = "%s.%s" % (c, a)
						logger.debug(u"Searching mapping for {!r}", valueMappingKey)
						if valueMappingKey in VALUE_MAPPING:
							v = forceList(v)
							for i in range(len(v)):
								v[i] = VALUE_MAPPING[valueMappingKey].get(str(v[i]), v[i])

							if len(v) == 1:
								v = v[0]

							logger.debug("Mapping applied. Value: {!r}", v)

						if isinstance(v, (list, tuple)):
							v = u', '.join(forceUnicodeList(v))

						if item['Type'].startswith('varchar'):
							v = forceUnicode(v)
							maxLen = forceInt(item['Type'].split('(')[1].split(')')[0].strip())

							if len(v) > maxLen:
								logger.warning(u"Truncating value {!r}: string is too long (maximum length: {})", v, maxLen)
								v = v[:maxLen]
								logger.debug(u"New value: {!r}", v)

						if v is not None:
							break

				opsiValues[opsiName][-1][item['Opsi']] = v

			logger.debug(u"Hardware object is now: {!r}", opsiValues[opsiName][-1])
			if not opsiValues[opsiName][-1]:
				logger.info(u"Skipping empty object")
				opsiValues[opsiName].pop()

	return opsiValues


def getHardwareInformationFromRegistry(conf, opsiValues={}):
	from OPSI.System.Windows import HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, getRegistryValue

	regex = re.compile('^\[\s*([^\]]+)\s*\]\s*(\S+.*)\s*$')
	for oneClass in conf:
		if not oneClass.get('Class') or not oneClass['Class'].get('Opsi'):
			continue

		opsiName = oneClass['Class']['Opsi']
		for item in oneClass['Values']:
			registryQuery = item.get('Registry')
			if not registryQuery:
				continue

			logger.info(u"Querying: %s" % registryQuery)
			match = re.search(regex, registryQuery)
			if not match:
				logger.error(u"Bad registry query '%s'" % registryQuery)
				continue

			logger.info(match)
			key = match.group(1)
			if not key.find('\\'):
				logger.error(u"Bad registry query '%s'" % registryQuery)
				continue

			(key, subKey) = key.split('\\', 1)
			valueName = match.group(2)

			if key in ('HKEY_LOCAL_MACHINE', 'HKLM'):
				key = HKEY_LOCAL_MACHINE
			elif key in ('HKEY_CURRENT_USER', 'HKCU'):
				key = HKEY_CURRENT_USER
			else:
				logger.error(u"Unhandled registry key '%s'" % key)
				continue

			try:
				value = getRegistryValue(key, subKey, valueName)
			except Exception as error:
				logger.error(u"Failed to get '%s': %s" % (registryQuery, error))
				continue

			if isinstance(value, bytes):
				value = value.encode('utf-8')

			if opsiName not in opsiValues:
				opsiValues[opsiName].append({})

			for i in range(len(opsiValues[opsiName])):
				opsiValues[opsiName][i][item['Opsi']] = value

	return opsiValues


def getHardwareInformationFromExecuteCommand(conf, opsiValues={}):
	from OPSI.System.Windows import execute

	regex = re.compile("^#(?P<cmd>.*)#(?P<extend>.*)$")
	for oneClass in conf:
		if not oneClass.get('Class') or not oneClass['Class'].get('Opsi'):
			continue

		opsiName = oneClass['Class']['Opsi']
		for item in oneClass['Values']:
			cmdline = item.get('Cmd')
			if not cmdline:
				continue
			condition = item.get("Condition")
			if condition:
				val = condition.split("=")[0]
				r = condition.split("=")[1]
				if val and r:
					conditionregex = re.compile(r)
					conditionmatch = None

					logger.info("Condition found, try to find the Condition")
					for i in range(len(opsiValues[opsiName])):
						value = opsiValues[opsiName][i].get(val, "")
						if value:
							conditionmatch = re.search(conditionregex, value)

							if not conditionmatch:
								continue

			match = re.search(regex, cmdline)
			if not match:
				logger.error(u"Bad Cmd entry '%s'" % cmdline)
				continue
			matchresult = match.groupdict()
			executeCommand = matchresult.get("cmd")
			extend = matchresult.get("extend")

			logger.info(u"Executing: %s" % executeCommand)
			value = ''
			try:
				result = execute(executeCommand)
				if result and extend:
					res = result[0]
					value = eval("res%s" % extend)
			except Exception as error:
				logger.logException(error)
				logger.error("Failed to execute command: '%s' error: '%s'" % (executeCommand, error))
				continue

			if isinstance(value, bytes):
				value = value.encode('utf-8')

			if opsiName not in opsiValues:
				opsiValues[opsiName].append({})

			for i in range(len(opsiValues[opsiName])):
				opsiValues[opsiName][i][item['Opsi']] = value

	return opsiValues

def numstring2Dec(numstring, base=36):
	if numstring is None:
		return None
	result = 0
	multiplier = 1
	for char in reversed(numstring):
		if char > '@':
			result += (ord(char)-55)*multiplier
		else:
			result += (ord(char)-48)*multiplier
		multiplier *= base
	return result

def getWMIProperty(key, table, condition=None):
	wmiObj = wmi.WMI()
	wmiQuery = f"Select {key} from {table}"
	logger.info(f"performing query: {wmiQuery}")
	if not condition is None:
		wmiQuery = wmiQuery.join(" where ").join(condition)
	reply = wmiObj.query(wmiQuery)
	if len(reply) == 0:
		return None
	for prop in reply[0].Properties_:
		#print(prop.Name, prop.Value)
		if prop.Name == key:
			return prop.Value
	return None

def getDellExpressCode(conf, opsiValues={}):
	tasks = [('Manufacturer', 'Win32_ComputerSystem')]
	tasks.append(('SerialNumber', 'Win32_SystemEnclosure'))
	reply = []
	for task in tasks:
		reply.append(getWMIProperty(task[0], task[1]))

	#reply[0] = "asdfDEllasdf"
	#reply[1] = "2y4955j"
	value = ""
	if re.search("dell", reply[0].lower()) is None:
		logger.notice("Manufacturer is not DELL, no dellexpresscode stored.")
		return opsiValues
	value = numstring2Dec(reply[1])

	for oneClass in conf:
		if oneClass.get('Class') is None or oneClass['Class'].get('Opsi') is None:
			continue
		opsiName = oneClass['Class']['Opsi']
		if opsiName not in opsiValues:
			continue
		for item in oneClass['Values']:
			if item['Opsi'] == "dellexpresscode":
				for i in range(len(opsiValues[opsiName])):
					opsiValues[opsiName][i][item['Opsi']] = value
					logger.notice(f"stored dellexpresscode {value}")
	return opsiValues

def makehwaudit():
	if os.path.exists(os.path.join('C:', 'opsi.org', 'log')):
		logDir = os.path.join('C:', 'opsi.org', 'log')
	else:
		logDir = os.path.join('C:', 'tmp')

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

		logger.notice(u"Fetching opsi hw audit configuration")
		config = backend.auditHardware_getConfig()

		if os.name == "nt":
			logger.notice(u"Fetching hardware information from WMI")
			values = getHardwareInformationFromWMI(config)

			logger.notice(u"Fetching hardware information from Registry")
			values = getHardwareInformationFromRegistry(config, values)

			#logger.notice("Fetching hardware information from Executing Command")
			#values = getHardwareInformationFromExecuteCommand(config, values)

			logger.notice("Extracting dellexpresscode (if any)")
			values = getDellExpressCode(config, values)


			logger.info(u"Hardware information from WMI:\n%s" % objectToBeautifiedText(values))
			auditHardwareOnHosts = []
			for hardwareClass, devices in values.items():
				if hardwareClass == 'SCANPROPERTIES':
					continue

				for device in devices:
					data = {str(attribute): value for attribute, value in device.items()}
					data['hardwareClass'] = hardwareClass
					data['hostId'] = host_id

					auditHardwareOnHosts.append(AuditHardwareOnHost.fromHash(data))
		else:
			logger.notice(u"Running hardware inventory")
			auditHardwareOnHosts = auditHardware(config = config, hostId = username)

		logger.info(u"Obsoleting old hardware audit data")
		backend.auditHardwareOnHost_setObsolete(host_id)
		logger.notice(u"Sending hardware information to service")
		backend.auditHardwareOnHost_updateObjects(auditHardwareOnHosts)

	logger.notice(u"Exiting...")