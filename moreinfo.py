moreinfo = {'sgb_radio_callsign': ('sgb_radio_callsign',
                                   '''The Radio call sign binary data is decoded using the modified-Baudot code shown in Table 3.1a of document T.018. This enables 7 characters to be encoded with 6 bits per character using only 42 bits (6x7=42).
                                     The two highest bits are spare and shall be coded as 00. This data will be left justified
                                    with a modified-Baudot space (100100) being used where no character exists. 
                                    If no Radio call sign is available then insert a series of 7 spaces (100100) '''),

            'country_code': ('country_code', '''
           The country code is a three-digit decimal Maritime Identification Digit (MID) country code assigned by the International Telecommunication Union (ITU). 
           The MID country code and corresponding country names are available on the ITU website (www.itu.int).           
           '''),

            'rls_trunc': ('rls_trunc',
                          '''
                       Truncated RLS TAC or National RLS Number
            The 10-bit RLS truncated TAC or National RLS number is the last 3 decimal numbers in the TAC number data field, which allows a range of 1 to 999. The RLS beacon TAC number or National RLS number series are assigned as follows:	
            1000 series is <strong>reserved</strong> for EPIRBs (i.e. 1001 to 1999),
            2000 series is reserved for ELTs (i.e. 2001 to 2999), and
            3000 series is reserved for PLBs (i.e. 3001 to 3999).
            
            These are represented in the RLS messages as bits 41-42 indicating the beacon type series (EPIRB, ELT, or PLB) and a 10 bit (1-1024) TAC number which is added to the series to encode the full TAC number. (e.g., TAC 1042 would be encoded as “01” for EPIRB in bits 41 to 42 representing 1nnn, where “nnn” is “042” determined by “0000101010” in bits 43 to 52, and form a binary representation “00 0010 1010” of the decimal number “42”.  
            
            The last 30 numbers (i.e., National RLS Numbers 970 to 999) are set aside for National Use by Competent Authorities. That is full National RLS Numbers 1970 to 1999 for EPIRBs, 2970 to 2999 for ELTs and 3970 to 3999 for PLBs.
            
            
                       '''),

            'elt_dt_aircraftoperator': ('elt_dt_aircraftoperator', '''
       Aircraft operator designator (3 letters) can be encoded in 15 bits using a shortened form of the
       modified-Baudot code (i.e.: all letters in the modified-Baudot code are coded in 6 bits, with the first bit = "1".
       This first bit can, therefore, be deleted to form a 5-bit. 3 x 5 = 15 bits'''),

            'bch1': ('bch1','''<strong>21-BIT BCH CODE CALCULATION</strong><br>The BCH error-correcting code located at bits 86-106 is calculated from the first protected field of all 406 MHz messages (bits 25-85).  It is a shortened form of a (127,106) Bose-Chaudhuri-Hocquenghem (BCH) code.  
            The shortened form (82,61) consists of 61 bits of data followed by a 21-bit triple error-correcting code.  
            The code is used to detect and correct up to three errors in the entire 82-bit pattern (bits 25 through 106 of the 406 MHz message).  
             <br><br>If the 21 bit computed BCH on bits 25-85 does not match the encoded BCH in bits 86-106, then there are errors in bits 25-106 of the message.            
            '''),

            'bch2': ('bch2','''<strong>12-BIT BCH CODE CALCULATION</strong><br>The BCH error correcting code located at bits 133-144, calculated from the second protected field of the 406Mhz message (bits 107-132), is capable 
            of detecting and correcting up to two bit errors in the 38 bits from 107-144.  
            
             <br><br>If the 12 bit computed BCH on bits 107-132 does not match the encoded BCH in bits 133-144, then there are errors in bits 107-144.            
            '''),

            'natloc': ('natloc', '''National location protocol identification data is provided in a nationally-defined format in 18 bits of PDF-1. 
             <br>Position data, to 2-minute resolution, is given in PDF-1, with position offsets to 4-second resolution in PDF-2.<br>
             18-bit identification data consisting of a serial number assigned by the appropriate national authority (bits 41-58).          
           '''),

            }

