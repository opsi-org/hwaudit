# -*- coding: utf-8 -*-

import re
import wmi
import pywintypes
from typing import Dict

from OPSI.Backend.JSONRPC import JSONRPCBackend
from OPSI.Util import objectToBeautifiedText
from OPSI.Object import AuditHardwareOnHost
from OPSI.Types import (
	forceHardwareDeviceId, forceHardwareVendorId, forceInt, forceList,
	forceUnicode, forceUnicodeList)

from .windows_values import VALUE_MAPPING
from . import __version__
from .opsihwauditconf import OPSI_HARDWARE_CLASSES	#TODO: remove

from opsicommon.logging import logger

def getHardwareInformationFromWMI(conf):
	"""
	Extracts hardware information from WMI.

	This method performs a number of WMI queries regarding
	hardware and stores the replies in a dictionary.

	:param conf: Config extracted from the backend.
	:param opsiValues: Dictionary containing the results of the audit.

	:returns: Dictionary containing the results of the audit.
	"""

	wmiObj = wmi.WMI()

	opsiValues = {}

	for oneClass in conf:
		if oneClass.get('Class') is None or oneClass['Class'].get('Opsi') is None or oneClass['Class'].get('WMI') is None:
			continue

		opsiName = oneClass['Class']['Opsi']
		wmiQuery = oneClass['Class']['WMI']
		mapClass = ''

		mapSep = '&'
		temp = wmiQuery.split(mapSep)
		if len(temp) == 2:
			wmiQuery, mapClass = temp

		logger.info(u"Querying: %s", wmiQuery)
		objects = []
		try:
			if wmiQuery.startswith("namespace="):
				namespace, wmiQuery = wmiQuery.split(":", 1)
				namespace = namespace.split("=", 1)[1].strip()
				customWMI = wmi.WMI(namespace=namespace)
				objects = customWMI.query(wmiQuery)
			else:
				objects = wmiObj.query(wmiQuery)
			logger.devel(objects)
		except pywintypes.com_error as error:
			logger.error(u"Query failed: %s", error)
			continue

		# first element? make new array for multiple devices
		if opsiName not in opsiValues:
			opsiValues[opsiName] = []

		for obj in objects:
			wmiClass = obj.ole_object.GetObjectText_().split()[2]

			associator = None
			if mapClass:
				assoc = obj.associators(mapClass)
				if len(assoc) > 0:
					associator = assoc[0]

			opsiValues[opsiName].append({})
			for item in oneClass['Values']:
				v = None
				if item.get('WMI'):
					for attribute in item['WMI'].split('||'):
						attribute = attribute.strip()
						attrclass = wmiClass

						if '::' in attribute:
							(attrclass, attribute) = attribute.split('::', 1)

						meth = None
						if '.' in attribute:
							(attribute, meth) = attribute.split('.', 1)

						op = None
						match = re.search(r'^(\w+)([\*\/\+\-\%]\d.*)$', attribute)
						if match:
							attribute = match.group(1)
							op = match.group(2)

						if attrclass == wmiClass and hasattr(obj, attribute):
							v = getattr(obj, attribute)
						elif associator and hasattr(associator, attribute):
							v = getattr(associator, attribute)
						else:
							if associator is None:
								logger.warning(u"%s.%s: failed to get attribute '%s' from object '%s'", opsiName, item['Opsi'], attribute, obj.__repr__())
							else:
								logger.warning(u"%s.%s: failed to get attribute '%s' from objects %s", opsiName, item['Opsi'], attribute, [obj.__repr__(), associator.__repr__()])
							continue

						if isinstance(v, tuple) and len(v) == 1:
							v = v[0]

						if meth and v is not None:
							try:
								v = eval('v.%s' % meth)
							except Exception as evalError:
								logger.debug("Method '%s' on function value '%s' failed: '%s'", meth, v, evalError)
								logger.warning(u"Method '%s' failed on value '%s'", meth, v)

						if op and v is not None:
							try:
								v = eval('v%s' % op)
							except Exception as evalError:
								logger.debug("Operation '%s' on function value '%s' failed: '%s'", op, v, evalError)
								logger.warning(u"Operation '%s' failed on value '%s'", op, v)

						if item['Opsi'] in ('vendorId', 'subsystemVendorId'):
							try:
								v = forceHardwareVendorId(v)
							except ValueError as hwVendError:
								logger.debug("Forcing hardware vendor id on '%s' failed: %s", v, hwVendError)
								v = None
						elif item['Opsi'] in ('deviceId', 'subsystemDeviceId'):
							try:
								v = forceHardwareDeviceId(v)
							except ValueError as hwDevError:
								logger.debug("Forcing hardware device id on '%s' failed: %s", v, hwDevError)
								v = None

						if v is None:
							continue

						if isinstance(v, str):
							v = forceUnicode(v.strip())
						#if isinstance(v, bytes):
						#	v = v.strip()

						valueMappingKey = "%s.%s" % (attrclass, attribute)
						logger.debug(u"Searching mapping for '%s'", valueMappingKey)
						if valueMappingKey in VALUE_MAPPING:
							v = forceList(v)
							for i in range(len(v)):
								v[i] = VALUE_MAPPING[valueMappingKey].get(str(v[i]), v[i])

							if len(v) == 1:
								v = v[0]

							logger.debug("Mapping applied. Value:'%s'", v)

						if isinstance(v, (list, tuple)):
							v = u', '.join(forceUnicodeList(v))

						if item['Type'].startswith('varchar'):
							v = forceUnicode(v)
							maxLen = forceInt(item['Type'].split('(')[1].split(')')[0].strip())

							if len(v) > maxLen:
								logger.warning(u"Truncating value '%s': string is too long (maximum length: %d)", v, maxLen)
								v = v[:maxLen]
								logger.debug(u"New value: '%s'", v)

						if v is not None:
							break

				opsiValues[opsiName][-1][item['Opsi']] = v

			logger.debug(u"Hardware object is now: '%s'", opsiValues[opsiName][-1])
			if not opsiValues[opsiName][-1]:
				logger.info(u"Skipping empty object")
				opsiValues[opsiName].pop()

	return opsiValues


def getHardwareInformationFromRegistry(conf, opsiValues):
	"""
	Extracts hardware information from the registry.

	This method queries the windows registry for hardware specification.
	Results are integrated into a dictionary.

	:param conf: Config extracted from the backend.
	:param opsiValues: Dictionary containing the results of the audit.

	:returns: Dictionary containing the results of the audit.
	"""
	from OPSI.System.Windows import HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, getRegistryValue

	regex = re.compile(r'^\[\s*([^\]]+)\s*\]\s*(\S+.*)\s*$')
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
				logger.error(u"Bad registry query '%s'", registryQuery)
				continue

			logger.info(match)
			key = match.group(1)
			if not key.find('\\'):
				logger.error(u"Bad registry query '%s'", registryQuery)
				continue

			(key, subKey) = key.split('\\', 1)
			valueName = match.group(2)

			if key in ('HKEY_LOCAL_MACHINE', 'HKLM'):
				key = HKEY_LOCAL_MACHINE
			elif key in ('HKEY_CURRENT_USER', 'HKCU'):
				key = HKEY_CURRENT_USER
			else:
				logger.error(u"Unhandled registry key '%s'", key)
				continue

			try:
				value = getRegistryValue(key, subKey, valueName)
			except OSError as error:
				logger.error(u"Failed to get '%s': %s", registryQuery, error)
				continue

			if isinstance(value, bytes):
				value = value.encode('utf-8')

			if opsiName not in opsiValues:
				opsiValues[opsiName].append({})

			for i in range(len(opsiValues[opsiName])):
				opsiValues[opsiName][i][item['Opsi']] = value

	return opsiValues

#TODO: deprecated (4.2.0.1 at 05.06.2020) - dellexpresscode.exe from lazarus now integrated in hwaudit.py
def getHardwareInformationFromExecuteCommand(conf, opsiValues):
	logger.warning("use of deprecated function getHardwareInformationFromExecuteCommand")
	from OPSI.System.Windows import execute

	regex = re.compile(r"^#(?P<cmd>.*)#(?P<extend>.*)$")
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
				logger.error(u"Bad Cmd entry '%s'", cmdline)
				continue
			matchresult = match.groupdict()
			executeCommand = matchresult.get("cmd")
			extend = matchresult.get("extend")

			logger.info(u"Executing: %s", executeCommand)
			value = ''
			try:
				result = execute(executeCommand)
				if result and extend:
					res = result[0]
					value = eval("res%s" % extend)
			except Exception as error:
				logger.logException(error)
				logger.error("Failed to execute command: '%s' error: '%s'", executeCommand, error)
				continue

			if isinstance(value, bytes):
				value = value.encode('utf-8')

			if opsiName not in opsiValues:
				opsiValues[opsiName].append({})

			for i in range(len(opsiValues[opsiName])):
				opsiValues[opsiName][i][item['Opsi']] = value

	return opsiValues

def numstring2Dec(numstring: str, base: int = 36) -> int:
	"""
	Comutes decimal representation.

	This method takes a number string containing digits and letters
	which is interpreted as a base <something> (default 36) number.
	A decimal representation is computed and returned.

	:param numstring: Input number in base <something> system. e.g. '123xyz'.
	:type numstring: str
	:param base: Base of the number system (default 36).
	:type base: int

	:returns: Decimal representation of the input.
	"""
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

def getWMIProperty(key: str, table: str, condition: str = None) -> str:
	"""
	Retrieves WMI properties.

	This method gets a key which it tries to query from an also given
	table with an optional condition.

	:param key: This key should be retrieved from a table in WMI.
	:type key: str
	:param table: The key is queried from this table.
	:type table: str
	:param condition: If provided this condition is tested in the query.
	:type condition: str

	:returns: value containing the reply on the query.
	"""
	wmiObj = wmi.WMI()
	wmiQuery = f"Select {key} from {table}"
	if not condition is None:
		wmiQuery = wmiQuery.join(" where ").join(condition)
	logger.info("performing query: %s", wmiQuery)
	reply = wmiObj.query(wmiQuery)
	if len(reply) == 0:
		return None
	for prop in reply[0].Properties_:
		#print(prop.Name, prop.Value)
		if prop.Name == key:
			return prop.Value
	return None

def getDellExpressCode(conf, opsiValues):
	"""
	Extracts the DELL expresscode.

	This method queries WMI for the Manufacturer. If it is DELL,
	the DELL expresscode is queried, converted to decimal and stored.

	:param conf: Config extracted from the backend.
	:param opsiValues: Dictionary containing the results of the audit.

	:returns: Dictionary containing the results of the audit.
	"""
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

def makehwaudit(backendConfig: Dict[str, str]) -> None:
	"""
	Performs a hardware audit.

	This method extracts information about the hardware from the backend config,
	WMI and the registry. The results are sent to and stored at the backend.

	:param backendConfig: Dictionary containing the configuration of the backend.
	:type backendConfig: dict
	"""
	with JSONRPCBackend(**backendConfig) as backend:
		logger.notice(u"Connected to opsi server")

		logger.notice(u"Fetching opsi hw audit configuration")
		#config = backend.auditHardware_getConfig()
		config = OPSI_HARDWARE_CLASSES

		logger.notice(u"Fetching hardware information from WMI")
		values = getHardwareInformationFromWMI(config)

		logger.notice(u"Fetching hardware information from Registry")
		values = getHardwareInformationFromRegistry(config, values)

		#logger.notice("Fetching hardware information from Executing Command")
		#values = getHardwareInformationFromExecuteCommand(config, values)

		logger.notice("Extracting dellexpresscode (if any)")
		values = getDellExpressCode(config, values)


		logger.info(u"Hardware information from WMI:\n%s", objectToBeautifiedText(values))
		auditHardwareOnHosts = []
		for hardwareClass, devices in values.items():
			if hardwareClass == 'SCANPROPERTIES':
				continue

			for device in devices:
				data = {str(attribute): value for attribute, value in device.items()}
				data['hardwareClass'] = hardwareClass
				data['hostId'] = backendConfig.get('host_id')
				auditHardwareOnHosts.append(AuditHardwareOnHost.fromHash(data))

		logger.info(u"Obsoleting old hardware audit data")
		backend.auditHardwareOnHost_setObsolete(backendConfig.get('host_id'))
		logger.notice(u"Sending hardware information to service")
		backend.auditHardwareOnHost_updateObjects(auditHardwareOnHosts)