from .hwaudit import makehwaudit

def main():
	#logger.setConsoleLevel(LOG_ERROR)
	#try:
	makehwaudit()
	#except Exception as error:
	#	logger.logException(error)
	#	sys.exit(1)


if __name__ == "__main__":
	main()