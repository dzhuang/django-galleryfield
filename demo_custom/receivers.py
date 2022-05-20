from django.db.models import FileField
from django.db.models.signals import post_save, pre_save
from django.dispatch.dispatcher import receiver

from demo_custom.models import CustomDemoGallery, CustomImage


@receiver(pre_save, sender=CustomDemoGallery)
def send_to_sendfile_on_gallery_save(sender, instance: CustomDemoGallery, **kwargs):
    for image in instance.images.objects.all():
        image.save_to_protected_storage()


# {{{ Delete temp image when it is saved to sendfile storage
# Ref https://www.algotech.solutions/blog/python/deleting-unused-django-media-files/


def delete_files(files_list: list) -> None:
    for file_ in files_list:
        if file_ and hasattr(file_, "storage") and hasattr(file_, "path"):
            # this accounts for different file storages
            # (e.g. when using django-storages)
            storage_, path_ = file_.storage, file_.path
            storage_.delete(path_)


@receiver(pre_save, sender=CustomImage)
def set_instance_cache(sender, instance: CustomImage, **kwargs):
    # stop if the object is not created.
    if instance.pk is None:
        return

    # preserve file if the temp image is cropped or rotated,
    # those file should be removed with the instances they belong to
    if instance.is_temp_image:
        return
    # prevent errors when loading files from fixtures
    from_fixture = "raw" in kwargs and kwargs["raw"]
    if not from_fixture:
        old_instance = sender.objects.filter(pk=instance.id).first()
        if old_instance is not None:
            # for each FileField, we will keep
            # the original value inside an ephemeral `cache`
            instance.files_cache = {
                field_.name: getattr(old_instance, field_.name, None)
                for field_ in sender._meta.fields
                if isinstance(field_, FileField)
            }


@receiver(post_save, sender=CustomImage)
def handle_files_on_update(
        sender, instance: CustomImage, **kwargs) -> None:

    if hasattr(instance, "files_cache") and instance.files_cache:
        deletables = []
        for field_name in instance.files_cache:
            old_file_value = instance.files_cache[field_name]
            new_file_value = getattr(instance, field_name, None)
            # only delete the files that have changed
            if old_file_value and old_file_value != new_file_value:
                deletables.append(old_file_value)
        delete_files(deletables)
        instance.files_cache = {
            field_name: getattr(instance, field_name, None)
            for field_name in instance.files_cache}

# }}}
