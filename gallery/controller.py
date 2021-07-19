import json

from .conf import *


def manage_images(sender, instance, **kwargs):
    # Receiver of Django post_save signal.
    # At this point we know that the model instance has been saved into the db.
    from .fields import GalleryField
    fields = [field for field in sender._meta.fields if type(field) in [GalleryField]]

    for field in fields:
        old_value_attr = OLD_VALUE_STR % field.name
        deleted_value_attr = DELETED_VALUE_STR % field.name
        moved_value_attr = MOVED_VALUE_STR % field.name
        if not hasattr(instance, old_value_attr):
            continue

        old_images = (getattr(instance, old_value_attr) or [])
        if old_images:
            if isinstance(old_images, str):
               old_images = json.loads(old_images)
        if not old_images:
            old_images = []

        current_images = (getattr(instance, field.name) or [])

        # This happens when delete all images from an instance
        if current_images == "null":
            current_images = []
        else:
            current_images = json.loads(current_images)

        assert isinstance(current_images, list)

        deleted_images = (getattr(instance, deleted_value_attr) or [])
        moved_images = (getattr(instance, moved_value_attr) or [])
        new_images = []
        changed = False

        for img in current_images:
            new_images.append(img)

        for img in deleted_images:
            # todo remove those img
            pass

        for img in old_images:
            if img not in current_images and img not in deleted_images and img not in moved_images:
                changed = True
                new_images.append(img)

        delattr(instance, old_value_attr)
        delattr(instance, deleted_value_attr)
        delattr(instance, moved_value_attr)

        if changed:
            setattr(instance, field.name, new_images)
            instance.save()
