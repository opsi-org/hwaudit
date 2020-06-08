import sys

def main():
	RUNS_ON_WINDOWS = sys.platform in ('nt', 'win32')
	if RUNS_ON_WINDOWS:
		from .hwaudit import makehwaudit
	else:
		from .hwinvent import makehwaudit
	makehwaudit()

if __name__ == "__main__":
	main()