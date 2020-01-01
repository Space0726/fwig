import constants as mfc

with open("./output.mf", 'w') as file_:
    with mfc.BeginChar(file_, '1234', 100, 100, 0) as bc:
        bc.add_body('x1 = 0;', 'x2 = 10;')
        with mfc.MfIf(file_, "10 > 15", 1) as mf_if:
            mf_if.add_body('x3 = 100;')
