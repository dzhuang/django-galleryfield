from django.db import transaction
from django.db.models import FileField
from django.db.models.signals import post_delete, post_save
from django.dispatch.dispatcher import receiver

from demo_custom.models import CustomDemoGallery, CustomImage


@receiver(post_save, sender=CustomDemoGallery)
@transaction.atomic
def refresh_gallery_image_set(
        sender, created, instance: CustomDemoGallery, **kwargs):
    related_images = instance.related_images

    # CustomImage objects which were in the gallery but now were removed
    images_to_delete = list(related_images.exclude(pk__in=list(instance.images)))

    # Clear and update the m2m relationship to the latest value
    related_images.clear()
    instance.related_images.set(instance.images.objects.all())

    # Delete CustomImage objects which don't belong to other gallery instance
    for image in images_to_delete:
        if not image.gallery.count():
            image.delete()


# {{{ Delete files when delete model instance
# https://cmljnelson.blog/2020/06/22/delete-files-when-deleting-models-in-django/


def delete_file_if_unused(model, instance, field, instance_file_field):
    """ Only delete the file if no other instances of that model are using it"""
    dynamic_field = dict()
    dynamic_field[field.name] = instance_file_field.name
    other_refs_exist = model.objects.filter(
        **dynamic_field).exclude(pk=instance.pk).exists()
    if not other_refs_exist:
        instance_file_field.delete(False)


@receiver(post_delete, sender=CustomImage)
def delete_files_when_row_deleted_from_db(sender, instance, **kwargs):
    """ Whenever ANY model is deleted, if it has a file field on it,
    delete the associated file too"""

    for field in sender._meta.concrete_fields:
        if isinstance(field, FileField):
            instance_file_field: FileField = getattr(instance, field.name)
            delete_file_if_unused(sender, instance, field, instance_file_field)

# }}}
