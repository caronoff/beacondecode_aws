moreinfo = {'full_message_SGB_ref':('full_message_SGB_ref',
                                    '''
<strong>23 Hex ID bits map to the respective bits in the complete beacon message per table below:</strong>
<br>
<br>
<br>
<table>
  <tr>
    <th>23 Hex ID Bit</th>
    <th>No Bits</th>
    <th>Bits Full Message</th>
    <th>Data Content</th>
  </tr>
  <tr>
    <td>1</td>
    <td>1</td>
    <td>n/a</td>
    <td>Binary '1'</td>
  </tr>
  
   <tr>
    <td>2 to 11</td>
    <td>10</td>
    <td>31 to 40</td>
    <td>Country Code</td>
  </tr>
  
  
   <tr>
    <td>12</td>
    <td>1</td>
    <td>n/a</td>
    <td>Binary '1'</td>
  </tr>
  
   <tr>
    <td>13</td>
    <td>1</td>
    <td>n/a</td>
    <td>Binary '0'</td>
  </tr>
  
   <tr>
    <td>14</td>
    <td>1</td>
    <td>n/a</td>
    <td>Binary '1'</td>
  </tr>
  
   <tr>
    <td>15-30</td>
    <td>16</td>
    <td>1-16</td>
    <td>C/S TAC No</td>
  </tr>
  
  
   <tr>
    <td>31-44</td>
    <td>14</td>
    <td>17-30</td>
    <td>Bcn S/N</td>
  </tr>
  
  
   <tr>
    <td>45</td>
    <td>1</td>
    <td>43</td>
    <td>Test Protocol</td>
  </tr>
  
  
   <tr>
    <td>46-48</td>
    <td>3</td>
    <td>91-93</td>
    <td>Vessel Id Type</td>
  </tr>
  
  
   <tr>
    <td>49-92</td>
    <td>44</td>
    <td>94-137</td>
    <td>Vessel Id</td>
  </tr>
  <tr>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  
   <tr>
    <td>Total</td>
    <td>92</td>
    <td></td>
    <td>23 Hex Id</td>
  </tr>
  
</table>





'''),




    'sgb_radio_callsign': ('sgb_radio_callsign',
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
            The 10-bit RLS truncated TAC or National RLS number is the last 3 decimal numbers in the TAC number data field, which allows a range of 1 to 949. The RLS beacon TAC number or National RLS number series are assigned as follows:	
            1000 series is <strong>reserved</strong> for EPIRBs (i.e. 1001 to 1949),
            2000 series is reserved for ELTs (i.e. 2001 to 2949), and
            3000 series is reserved for PLBs (i.e. 3001 to 3949).
            
            These are represented in the RLS messages as bits 41-42 (except when bits 43 to 46 are set to 1111) indicating the beacon type series (EPIRB, ELT, or PLB) and a 10 bit (1-1024) TAC number which is added to the series to encode the full TAC number. (e.g., TAC 1042 would be encoded as 01 for EPIRB in bits 41 to 42 representing 1nnn, where nnn is 042 determined by 0000101010 in bits 43 to 52, and form a binary representation 00 0010 1010 of the decimal number 42.            
            The last numbers 920-949(i.e., National RLS Numbers 920 to 949) are set aside for National Use by Competent Authorities. That is full National RLS Numbers 1920-1949 for EPIRBs, 2920-2949 for ELTs and 3920-3949 for PLBs.
                       
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
             <br>If the message is a long message, position data to 2-minute resolution is given in PDF-1, with position offsets to 4-second resolution in PDF-2.<br>
             18-bit identification data consisting of a serial number assigned by the appropriate national authority (bits 41-58).          
           '''),
            'protocol_flag':('protocol_flag',''' The protocol flag (bit 26) indicates which type of protocol is used to define the structure of encoded data, according to the following code:
Bit 26 set to 0 is Location protocols which includes  Standard location,  National location, RLS location or ELT-DT location.
When bit 26 is set to 1,  User protocols or User-location protocols is used. ''')

            }

