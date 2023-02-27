# This script will convert CrealitySlicer Laser Gcode for use with mriscoc/Ender3V2S1 Pro firmware.
# It will convert all Inline laser power control G0/G1 commands to M3 commands immediately preceeding their respective moves, 
# including an 8-bit unsigned int conversion from Creality's 0-999 range for laser power

import sys

file_name = sys.argv[1] 
debug = False							# change debug to True if you want to see every line that has been altered

with open(file_name, 'r+') as f:
    print("Reading File. Please wait...")
    content = f.readlines()  					# gcode as a list where each element is a line 
    new_code = ""
    print("...done. Begin line parsing...")
    for line in content: 
        if "M3 I" in line:	# Remove the M3 Inline Power mode command
            if debug: print("Removed 'M3 I'")
            pass
        elif "M5" in line:	# Convert M5 I to just M5
            new_code += "M5" + '\n'
            if debug: print("Converted 'M5 I' to 'M5'")
        elif line[0] != "G":	# Not a move line; keep this line unchanged
            new_code += line	
        else:			# Is a move line; break it into parts to check for inline power
            gcode = ""						
            comment = ""						
            new_gcode = ""						
            power = ""						
            new_power = ""						
            if ";" in line:
                gcode, comment = line.strip('\n').split(";") 	# preserve the comment
            else:
                gcode = line.strip('\n')			# no comment, just remove newline
            if "S" in gcode:
                new_gcode, power = gcode.split("S",1)		# extract inline power
                new_power = int(int(power)//3.91)			# divide Creality's 0-999 power value by 3.91 to get 8-bit int for M3 power value
                new_code += "M3 O" + str(new_power) + '\n'	# write M3 line to change power level before next move
                if comment != "":
                    new_code += new_gcode + ' ; ' + comment + '\n'  # write gcode and comment without inline power
                    if debug:
                        print("Line: " + line.strip('\n'))
                        print("Changed to:")
                        print(" M3 0" + str(new_power))
                        print(" " + new_gcode + " ; " + comment + '\n')
                else: 
                    new_code += new_gcode + '\n'
                    if debug:
                        print("Line: " + line.strip('\n'))
                        print("Changed to:")
                        print(" M3 0" + str(new_power))
                        print(" " + new_gcode + '\n')
            else:
                new_code += line				# no inline power found, keep this line unchanged

    print("...done. Writing changes to file. Please wait...")
    f.seek(0)           # set the cursor to the beginning of the file
    f.write(new_code)   # write the new code over the old one
    print("...DONE! Exiting.")
