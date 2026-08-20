def images(imageName):
    # remove spaces
    img_without_spaces=imageName.replace(" ","")
    img=img_without_spaces.replace("_","")
    extensions = ['mp4','MP4',"jpg", "JPG", 'png', 'PNG', 'gif', 'GIF', 'tiff', 'TIFF', 'heic','HEIC', 'jpeg', 'JPEG', 'jpg', 'JPG', 'jpe', 'JPE', 'jffif', 'JFFIF', 'bmp', 'BMP', 'dib', 'DIB','webp']

    # Case_1 is generally when the extension has three characters eg png,jpg etc
    # find the length of the image name plus extension
    case_1_length = len(img)
    # subtract three. The three is the number of character of the extension
    case_1 = case_1_length - 3
    # case_1_first_letter is the first letter of the extension
    case_1_first_letter = case_1
    # ================================
    # now case_1_extension is the extracted 3 letter extension from the last three digits
    case_1_extension = img[case_1_first_letter:case_1_length]
    # mycase_1_body is the actual name of the file
    mycase_1_body = img[0:case_1_first_letter]
    # if the filename(without extension) is > 10, we trim it
    if len(mycase_1_body)>50:
        case1_body=img[0:30]
    else:
        case1_body = img[0:case_1_first_letter]
    # ====================================

    # the above concept is applied in both case 2 and 3. Case 2 being extension with 4 characters, case 3 being extension with 5 characters

    case_2_length = len(img)
    case_2 = case_2_length - 4
    case_2_first_letter = case_2
    # ===============
    case_2_extension = img[case_2_first_letter:case_2_length]
    mycase_2_body = img[0:case_2_first_letter]
    if len(mycase_2_body)>50:
        case2_body=img[0:49]
    else:
        case2_body = img[0:case_2_first_letter]
    # =================


    case_3_length = len(img)
    case_3 = case_3_length - 5
    case_3_first_letter = case_3
    # =======================
    case_3_extension = img[case_3_first_letter:case_3_length]
    mycase_3_body = img[0:case_3_first_letter]
    if len(mycase_3_body)>40:
        case3_body=img[0:36]
    else:
        case3_body = img[0:case_3_first_letter]
    # ===================


    # Here is where the image name will be converted into base64 then merged with its extension
    import base64
    if case_1_extension in extensions:
        # only the body of the name, i.e excluding the extension, will be converted to base64
        #first we convert to ascii
        case_1_body= case1_body.encode("ascii")
        # convert to base64 and assign it to a variable,case_1_b64encbody
        case_1_b64encbody=base64.b64encode(case_1_body)
        # join the body(converted to base64) and the extension
        opt1 = f"{case_1_b64encbody}.{case_1_extension}"
        # convert the final name to lowercase
        opt_1=opt1.lower()
        # The same applies to case_2 and 3
        return opt_1
    elif case_2_extension in extensions:
        case_2_body = case2_body.encode("ascii")
        case_2_b64encbody = base64.b64encode(case_2_body)
        opt2 = f"{case_2_b64encbody}.{case_2_extension}"
        opt_2=opt2.lower()
        return opt_2
    elif case_3_extension in extensions:
        case_3_body = case3_body.encode("ascii")
        case_3_b64encbody = base64.b64encode(case_3_body)
        opt3=f"{case_3_b64encbody}.{case_3_extension}"
        opt_3=opt3.lower()
        return opt_3
    else:
        message="Extension not found Error"
        return message


