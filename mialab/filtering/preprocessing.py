"""The pre-processing module contains classes for image pre-processing.

Image pre-processing aims to improve the image quality (image intensities) for subsequent pipeline steps.
"""
import warnings

import pymia.filtering.filter as pymia_fltr
import SimpleITK as sitk
import numpy as np
import nibabel as nib

import os

from intensity_normalization.normalize import fcm
from intensity_normalization.normalize import whitestripe

class ImageNormalizationParameters(pymia_fltr.FilterParams):
    """Image registration parameters."""

    def __init__(self, path: dict, weighted: int):
        """Initializes a new instance of the ImageNormalizationParameters

        Args:
            path (dict): Path to current image.
            weighted (int): whether T1 or T2 weighted
        """
        self.path = path
        self.weighted = weighted

class ImageNormalization(pymia_fltr.Filter):
    """Represents a normalization filter."""

    def __init__(self):
        """Initializes a new instance of the ImageNormalization class."""
        super().__init__()

    def execute(self, image: sitk.Image, params: ImageNormalizationParameters = None) -> sitk.Image:
        """Executes a normalization on an image.

        Args:
            image (sitk.Image): The image.
            params (FilterParams): The parameters (unused).

        Returns:
            sitk.Image: The normalized image.
        """

        path = params.path
        weighted = params.weighted
        brain_mask = nib.load(os.path.join(path, 'Brainmasknative.nii.gz'))

        img_arr = sitk.GetArrayFromImage(image)

        # todo: normalize the image using numpy
        #warnings.warn('No normalization implemented. Returning unprocessed image.')
        n_type = "histMatching"

        #sitk.Normalize(image)

        # Z Score Normalization
        if n_type == "zScore":
            img_arr = (img_arr - img_arr.mean()) / img_arr.std()

        # MinMax Normalization
        if n_type == "minMax":
            img_arr = (img_arr - np.min(img_arr)) / (np.max(img_arr) - np.min(img_arr))

        img_out = sitk.GetImageFromArray(img_arr)
        img_out.CopyInformation(image)

        # sitk Normalization 
        if n_type == "sitkN":
            img_out = sitk.Normalize(image)

        # Whitestripe Normalization
        if n_type == "whitestripe":
            img = None
            contrast = None

            if weighted == 1:
                img = nib.load(os.path.join(path, 'T1native.nii.gz'))
                contrast = 'T1'
            elif weighted == 2:
                img = nib.load(os.path.join(path, 'T2native.nii.gz'))
                contrast = 'T2'
            indices = whitestripe.whitestripe(img, contrast, mask=brain_mask)
            normalized = whitestripe.whitestripe_norm(img, indices)

            nib.save(normalized, os.path.join(path, 'wsnormalized.nii.gz'))
            img_out = sitk.ReadImage(os.path.join(path, 'wsnormalized.nii.gz'))

            if os.path.exists(os.path.join(path, 'wsnormalized.nii.gz')):
                os.remove(os.path.join(path, 'wsnormalized.nii.gz'))

        # Fuzzy-C Means Normalization
        if n_type == "fcm":
            img = None

            if weighted == 1:
                img = nib.load(os.path.join(path, 'T1native.nii.gz'))
            elif weighted ==2:
                img = nib.load(os.path.join(path, 'T2native.nii.gz'))
            
            # find the mask of this tissue type (wm, gm, or csf)
            wm_mask = fcm.find_tissue_mask(img, brain_mask, tissue_type="wm")
            normalized = fcm.fcm_normalize(img, wm_mask)

            nib.save(normalized, os.path.join(path, 'fcmnormalized.nii.gz'))
            img_out = sitk.ReadImage(os.path.join(path, 'fcmnormalized.nii.gz'))

            if os.path.exists(os.path.join(path, 'fcmnormalized.nii.gz')):
                os.remove(os.path.join(path, 'fcmnormalized.nii.gz'))
            

        # Histogram Matching Normalization
        if n_type == "histMatching":
            refImg = None

            allDataPath = os.path.dirname(path)
            firstFolder = os.listdir(allDataPath)[0]
            if weighted == 1:
                refImg = sitk.ReadImage(os.path.join(allDataPath, firstFolder, 'T1native.nii.gz'))
            elif weighted == 2:
                refImg = sitk.ReadImage(os.path.join(allDataPath, firstFolder, 'T2native.nii.gz'))

            img_out = sitk.HistogramMatching(image, refImg)
        return img_out

    def __str__(self):
        """Gets a printable string representation.

        Returns:
            str: String representation.
        """
        return 'ImageNormalization:\n' \
            .format(self=self)


class SkullStrippingParameters(pymia_fltr.FilterParams):
    """Skull-stripping parameters."""

    def __init__(self, img_mask: sitk.Image):
        """Initializes a new instance of the SkullStrippingParameters

        Args:
            img_mask (sitk.Image): The brain mask image.
        """
        self.img_mask = img_mask


class SkullStripping(pymia_fltr.Filter):
    """Represents a skull-stripping filter."""

    def __init__(self):
        """Initializes a new instance of the SkullStripping class."""
        super().__init__()

    def execute(self, image: sitk.Image, params: SkullStrippingParameters = None) -> sitk.Image:
        """Executes a skull stripping on an image.

        Args:
            image (sitk.Image): The image.
            params (SkullStrippingParameters): The parameters with the brain mask.

        Returns:
            sitk.Image: The normalized image.
        """
        mask = params.img_mask  # the brain mask

        # todo: remove the skull from the image by using the brain mask
        # warnings.warn('No skull-stripping implemented. Returning unprocessed image.')

        filter = sitk.MaskImageFilter()
        image = filter.Execute(image, mask)

        # reference_img = image
        # mask_np = sitk.GetArrayFromImage(mask).astype(bool)
        # image_np = sitk.GetArrayFromImage(image)
        # image_np *= mask_np
        # image = sitk.GetImageFromArray(image_np)
        # image.CopyInformation(reference_img)     

        return image

    def __str__(self):
        """Gets a printable string representation.

        Returns:
            str: String representation.
        """
        return 'SkullStripping:\n' \
            .format(self=self)


class ImageRegistrationParameters(pymia_fltr.FilterParams):
    """Image registration parameters."""

    def __init__(self, atlas: sitk.Image, transformation: sitk.Transform, is_ground_truth: bool = False):
        """Initializes a new instance of the ImageRegistrationParameters

        Args:
            atlas (sitk.Image): The atlas image.
            transformation (sitk.Transform): The transformation for registration.
            is_ground_truth (bool): Indicates weather the registration is performed on the ground truth or not.
        """
        self.atlas = atlas
        self.transformation = transformation
        self.is_ground_truth = is_ground_truth


class ImageRegistration(pymia_fltr.Filter):
    """Represents a registration filter."""

    def __init__(self):
        """Initializes a new instance of the ImageRegistration class."""
        super().__init__()

    def execute(self, image: sitk.Image, params: ImageRegistrationParameters = None) -> sitk.Image:
        """Registers an image.

        Args:
            image (sitk.Image): The image.
            params (ImageRegistrationParameters): The registration parameters.

        Returns:
            sitk.Image: The registered image.
        """

        # todo: replace this filter by a registration. Registration can be costly, therefore, we provide you the
        # transformation, which you only need to apply to the image!
        #warnings.warn('No registration implemented. Returning unregistered image')

        atlas = params.atlas
        transform = params.transformation
        is_ground_truth = params.is_ground_truth  # the ground truth will be handled slightly different

        if is_ground_truth:
            image = sitk.Resample(image, atlas, transform, sitk.sitkLinear, 0.0, image.GetPixelID())
        else:
            image = sitk.Resample(image, atlas, transform, sitk.sitkLinear, 0.0, image.GetPixelID())

        # note: if you are interested in registration, and want to test it, have a look at
        # pymia.filtering.registration.MultiModalRegistration. Think about the type of registration, i.e.
        # do you want to register to an atlas or inter-subject? Or just ask us, we can guide you ;-)

        return image

    def __str__(self):
        """Gets a printable string representation.

        Returns:
            str: String representation.
        """
        return 'ImageRegistration:\n' \
            .format(self=self)
