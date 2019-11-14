#!/usr/bin/env python3

import sys
import re
import imagetool

def main():
    try:
        imagetool.real_main()
    except FileNotFoundError as error:
        print(error)
    except ValueError as error:
        print(error)
    except re.error:
        print('ERROR: --input-name not a valid REGEX.')
    except KeyboardInterrupt:
        print('')
        sys.exit()
    input('Press any key to continue...')
    sys.exit()

main()
