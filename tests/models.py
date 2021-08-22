from django.db import models

from galleryfield.fields import GalleryField


class FakeValidImageModel(models.Model):
    image = models.ImageField()


class DemoGalleryForTest(models.Model):
    images = GalleryField(target_model="tests.FakeValidImageModel")


# {{{ invalid models

class FakeInvalidImageModel1(models.Model):
    image = models.CharField(max_length=250)


class FakeInvalidImageModel2(models.Model):
    photo = models.ImageField()

    def get_image_field(self):
        return self.photo


class FakeInvalidImageModel3(models.Model):
    photo = models.CharField(max_length=250)

    @classmethod
    def get_image_field(cls):
        return cls._meta.get_field("photo")


class FakeInvalidImageModel4(models.Model):
    photo = models.CharField(max_length=250)

    @property
    def get_image_field(self):
        return self.photo


class FakeInvalidImageModel5(models.Model):
    photo = models.ImageField()

    @classmethod
    def get_image_field(cls):
        return cls._meta.get_field("image")


# }}}
