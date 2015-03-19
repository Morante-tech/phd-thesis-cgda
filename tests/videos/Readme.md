### Video Parameters

synthetic_test_1:

    * Network: Custom
    * ACTUAL_IMAGES = TRUE
    * ROWS_1 = int(20)
    * COLS_1 = int(ROWS_1 * frame1Cols / frame1Rows)
    * ROWS_2 = int(20)
    * COLS_2 = int(ROWS_2 * frame2Cols / frame2Rows)
    * ALPHA = np.float32(0.1) # small alpha. at least 1/10 of beta
    * BETA =  np.float32(1)
    * MS_TO_WAIT= 1
    * LOAD_FROM_FILE = False

tatup_test_1:

    * Network: Custom
    * ACTUAL_IMAGES = TRUE
    * ROWS_1 = int(20)
    * COLS_1 = int(ROWS_1 * frame1Cols / frame1Rows)
    * ROWS_2 = int(20)
    * COLS_2 = int(ROWS_2 * frame2Cols / frame2Rows)
    * ALPHA = np.float32(0.1) # small alpha. at least 1/10 of beta
    * BETA =  np.float32(1)
    * MS_TO_WAIT= 1
    * LOAD_FROM_FILE = False

