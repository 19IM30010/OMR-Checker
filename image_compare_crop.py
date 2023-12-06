import cv2
import numpy as np


def convert_to_option(answer_number):
    convert = {1: "A", 2: "B", 3: "C", 4: "D"}
    return convert[answer_number]


def numpy_array_to_cv2_image(numpy_array):
    # Convert the NumPy array to bytes
    _, buffer = cv2.imencode('.jpg', numpy_array)

    # Decode the bytes back to a cv2.imread object
    cv2_image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)

    return cv2_image


def modify_cropped_image(cropped_box_image):
    # Define lower and upper threshold values for gray, blue, and black
    lower_gray = np.array([100, 100, 100], dtype=np.uint8)
    upper_gray = np.array([150, 150, 150], dtype=np.uint8)

    lower_blue = np.array([0, 0, 100], dtype=np.uint8)
    upper_blue = np.array([100, 100, 255], dtype=np.uint8)

    lower_black = np.array([0, 0, 0], dtype=np.uint8)
    upper_black = np.array([50, 50, 50], dtype=np.uint8)

    # Create masks for each color range
    mask_gray = cv2.inRange(cropped_box_image, lower_gray, upper_gray)
    mask_blue = cv2.inRange(cropped_box_image, lower_blue, upper_blue)
    mask_black = cv2.inRange(cropped_box_image, lower_black, upper_black)

    # Combine masks
    combined_mask = cv2.bitwise_or(mask_gray, cv2.bitwise_or(mask_blue, mask_black))

    # Set pixels that match any of the masks to black, and others to white
    result_image = cv2.bitwise_and(cropped_box_image, cropped_box_image, mask=~combined_mask)
    result_image[np.where(combined_mask != 0)] = [255, 255, 255]

    return result_image


def process_cropped_image_box(cropped_box_image_n, num_questions, questions_per_box, num_boxes, box_number, ans_dict,
                              result_dict):
    # Assuming cropped_box_image is your NumPy array

    cropped_box_image = numpy_array_to_cv2_image(cropped_box_image_n)
    # cropped_box_image = modify_cropped_image(img)
    # trim 15 from bottom to remove partial answer
    # cropped_box_image = cropped_box_image[0:h - 15, 0:w]
    # cropped_box_image = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
    h, w, _ = cropped_box_image.shape
    print(h, w)
    # threshold on color
    lower = (0, 0, 0)  # Lower threshold values
    upper = (200, 200, 200)  # Upper threshold values
    # upper = (200, 200, 200)
    thresh = cv2.inRange(cropped_box_image, lower, upper)

    # apply morphology close
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (14, 14))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel)

    # find contours in the thresholded image
    contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    i = 1
    for contour in contours:
        # Calculate the centroid of the contour
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # Calculate distance from left and top edges
            distance_from_left = cx
            distance_from_top = cy
            denom = (h / questions_per_box)
            qt = ((distance_from_top + denom) / denom)
            qnum = round(qt) + (box_number - 1) * questions_per_box
            if distance_from_left <= w / 4:
                result_dict[qnum]["Written_ans"] = 'A'
                print("Question_no.: ", qnum, " Predicted_ans is A and Right Ans is: ",
                      convert_to_option(ans_dict[qnum]))
            elif distance_from_left <= (2 * w) / 4:
                result_dict[qnum]["Written_ans"] = 'B'
                print("Question_no.: ", qnum, " Predicted_ans is B and Right Ans is: ",
                      convert_to_option(ans_dict[qnum]))
            elif distance_from_left <= (3 * w) / 4:
                result_dict[qnum]["Written_ans"] = 'C'
                print("Question_no.: ", qnum, " Predicted_ans is C and Right Ans is: ",
                      convert_to_option(ans_dict[qnum]))
            elif distance_from_left <= w:
                result_dict[qnum]["Written_ans"] = 'D'
                print("Question_no.: ", qnum, " Predicted_ans is D and Right Ans is: ",
                      convert_to_option(ans_dict[qnum]))
            i += 1
    # Save and display the thresholded image
    cv2.imwrite(f'omr_box_{box_number}_thresh.png', thresh)
    cv2.imshow(f"Box {box_number} Thresholded Image", thresh)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# Example usage:
# Assuming you have cropped_box_images list, num_questions, questions_per_box, num_boxes, and ans_dict


def crop_boxes_from_image(boxes_data, cropped_uploaded_image):
    try:
        # Convert the cropped image to OpenCV format
        cropped_uploaded_image_np = np.array(cropped_uploaded_image)
        print("Hello")
        # Dictionary to store cropped images for each box
        cropped_box_images = {}

        # Process each box in the boxes_data
        for box_name, box_data in boxes_data.items():
            x1, y1, width, height = box_data['x1'], box_data['y1'], box_data['width'], box_data['height']

            # Crop the region from the aligned uploaded image based on box coordinates
            cropped_box_image = cropped_uploaded_image_np[y1:y1 + height, x1:x1 + width]

            # Store the cropped image in the dictionary
            cropped_box_images[box_name] = cropped_box_image

            # Display or further process the cropped box image as needed
            # cv2.imshow(f"Cropped Box {box_name}", cropped_box_image)

        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # You can do further processing or return the result as needed
        return cropped_box_images

    except Exception as e:
        print(f"Error cropping boxes from image: {str(e)}")
        return None


def sift_image_comparison(stored_image, uploaded_image):
    try:
        # Convert images to OpenCV format
        stored_image_np = np.array(stored_image)
        uploaded_image_np = np.array(uploaded_image)

        # Initialize the SIFT feature detector and descriptor
        sift = cv2.SIFT_create()

        # Detect key points and compute descriptors for the stored image and the uploaded image
        keypoints_stored, descriptors_stored = sift.detectAndCompute(stored_image_np, None)
        keypoints_uploaded, descriptors_uploaded = sift.detectAndCompute(uploaded_image_np, None)

        # Initialize the FLANN matcher
        flann = cv2.FlannBasedMatcher()

        # Match the descriptors of the stored image and the uploaded image
        matches = flann.knnMatch(descriptors_stored, descriptors_uploaded, k=2)

        # Filter the matches based on Lowe's ratio test
        good_matches = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good_matches.append(m)

        # Calculate the percentage of good matches
        percentage_good_matches = (len(good_matches) / len(matches)) * 100
        print("Percentage of good matches: {:.2f}%".format(percentage_good_matches))

        # Extract the matched keypoints of the stored image and the uploaded image
        matched_keypoints_stored = np.float32([keypoints_stored[m.queryIdx].pt for m in good_matches]).reshape(
            -1, 1, 2)
        matched_keypoints_uploaded = np.float32(
            [keypoints_uploaded[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # Find the perspective transformation (homography) between the matched keypoints
        transformation_matrix, _ = cv2.findHomography(matched_keypoints_uploaded, matched_keypoints_stored,
                                                      cv2.RANSAC)

        # Warp the uploaded image to align with the stored image
        aligned_uploaded_image = cv2.warpPerspective(uploaded_image_np, transformation_matrix,
                                                     (stored_image_np.shape[1], stored_image_np.shape[0]))

        # Crop the aligned uploaded image to match the size of the stored image
        cropped_uploaded_image = aligned_uploaded_image[:stored_image_np.shape[0], :stored_image_np.shape[1]]

        # Display the images using cv2.imshow
        # cv2.imshow("Stored Image", stored_image_np)
        # cv2.imshow("Uploaded Image", uploaded_image_np)
        # cv2.imshow("Aligned Uploaded Image", aligned_uploaded_image)
        cv2.imshow("Cropped Uploaded Image", cropped_uploaded_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        print(cropped_uploaded_image)
        # You can do further processing or return the result as needed

        return cropped_uploaded_image

    except Exception as e:
        print(f"Error performing SIFT image comparison: {str(e)}")
        return None
