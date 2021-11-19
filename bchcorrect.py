import bch1correct as bch1
import bch2correct as bch2
import decodefunctions as Fcn
import Gen2functions as Fcn2

def bch1_binarycalc(inputhex):
    try:
        bin=Fcn.hextobin(inputhex)
    except TypeError as err:
        return [inputhex + '  Is not a valid hex']

    result = ''

    if len(inputhex)==36:
        strhex = inputhex[6:]
        bin=bin[24:]
        result = Fcn.calcbch(bin, "1001101101100111100011", 0, 61, 82)

    elif len(inputhex)==30 :
        strhex = inputhex
        result = Fcn.calcbch(bin, "1001101101100111100011", 0, 61, 82)

    elif len(inputhex)==63 :
        # SGB recalc bch1
        strhex = inputhex
        result = Fcn2.calcBCH(bin[2:], 0, 202, 250)

    else:
        result = 'Invalid Input Hex length of ' + str(len(inputhex)) + '.' + ' Valid length of FGB 30/36  or  63 for SGB'

    return result






def bch2_binarycalc(inputhex):
    try:
        bin = Fcn.hextobin(inputhex)
    except TypeError as err:
        return [inputhex + '  Is not a valid hex']

    result = ''

    if len(inputhex) == 36:
        strhex = inputhex[6:]
        bin = bin[24:]
        result = Fcn.calcbch(bin, '1010100111001', 82, 108, 120)

    elif len(inputhex) == 30:
        strhex = inputhex
        result = Fcn.calcbch(bin, '1010100111001', 82, 108, 120)

    elif len(inputhex) ==63 :
        return ""

    else:
        result = 'Invalid Input Hex length of ' + str(len(inputhex)) + '.' + ' Valid lengths of FGB message are 30 or 36'

    return result




def bch_recalc(inputhex):
    results = [inputhex]
    preamble =''
    if len(inputhex)==36:
        strhex = inputhex[6:]
        preamble = inputhex[:6]
    elif len(inputhex)==30:
        strhex = inputhex
        preamble =''
    else:
        type = 'Hex length of ' + str(len(inputhex)) + '.' + ' Length of First Generation Beacon Hex Code to test BCH must be 30 or 36'

        return [type]

    try:
        bin=Fcn.hextobin(strhex)
        _pdf1 = (bin)[:61]
        _bch1 = (bin)[61:82]
        _pdf2 = (bin)[82:108]
        _bch2 = (bin)[108:]

        bch1calc = Fcn.calcbch(bin, "1001101101100111100011", 0, 61, 82)
        bch2calc = Fcn.calcbch(bin, '1010100111001', 82, 108, 120)

        if _pdf1+bch1calc+_pdf2+bch2calc == bin:
            results.append('bch1 and bch2 recomputed from provided pdf1 and pdf2 match')
        else:
            if bch1calc!=_bch1:
                results.append('bch1 recomputed from provided pdf1 in input message {}'.format(bch1calc))
            if bch2calc!=_bch2:
                results.append('bch2 recomputed from provided pdf2 in input message {}'.format(bch2calc))
            results.append(preamble+Fcn.bin2hex(_pdf1 + bch1calc + _pdf2 + bch2calc))
        return results



    except TypeError as err:
        return [inputhex + '  Is not a valid hex']





def bch_check(inputhex):
    errors = [inputhex]
    preamble =''
    if len(inputhex)==36:
        strhex = inputhex[6:]
        preamble = inputhex[:6]
    elif len(inputhex)==30:
        strhex = inputhex
        preamble =''
    else:
        return False
    ## Error correction attempt for when BCH portion does not match recomputed
    try:
        _pdf1 = (Fcn.hextobin(strhex))[:61]
        _bch1 = (Fcn.hextobin(strhex))[61:82]
        bitflips1, newpdf1, newbch1 = bch1.pdf1_to_bch1(_pdf1, _bch1)
        _pdf2 = (Fcn.hextobin(strhex))[82:108]
        _bch2 = (Fcn.hextobin(strhex))[108:]
        bitflips2, newpdf2, newbch2 = bch2.pdf2_to_bch2(_pdf2, _bch2)
        if bitflips1 == -1 or bitflips2 == -1:
            errors.append('Too many bit errors to correct')
        elif bitflips1 > 0 or bitflips2 > 0:
            _newbin = newpdf1 + newbch1 + newpdf2 + newbch2
            fixhex= preamble+ Fcn.bin2hex(_newbin)
            errors.append(fixhex)
            errors.append(' {} bad pdf1 bit and {} bad pdf2 bit'.format(bitflips1, bitflips2))
            errors.append('Corrected Message: {} '.format(fixhex))
    except:
        return False


    return errors


if __name__ == "__main__":
    strhex = input("Hex message: ")

    errors=[]
    #errors = bch_recalc(strhex)

    if errors:
        print(errors)

    _pdf1 = (Fcn.hextobin(strhex))[:61]
    print(len(_pdf1))
    _bch1 = (Fcn.hextobin(strhex))[61:82]
    bitflips1, newpdf1, newbch1 = bch1.pdf1_to_bch1(_pdf1, _bch1)
    _pdf2 = (Fcn.hextobin(strhex))[82:108]
    _bch2 = (Fcn.hextobin(strhex))[108:]
    bitflips2, newpdf2, newbch2 = bch2.pdf2_to_bch2(_pdf2, _bch2)
    if bitflips1 == -1 or bitflips2 == -1:
        print('Too many bit errors to correct')
    elif bitflips1 > 0 or bitflips2 > 0:
        _newbin = newpdf1 + newbch1 + newpdf2 + newbch2
        print(' {} bad pdf1 bit and {} bad pdf2 bit'.format(bitflips1, bitflips2))
        print('Corrected Message: {} '.format(Fcn.bin2hex(_newbin)))
        print(_newbin, len(_newbin), len(newpdf1), len(newbch1), len(newpdf2), len(newbch2))
    else:
        print('bch1 and bch2 encoded match recalculated')
    print('-'*50)
    print(bch1_binarycalc(strhex))
    print(bch2_binarycalc(strhex))

