import json
from gallery import conf


def manage_images(sender, instance, **kwargs):
    # Receiver of Django post_save signal.
    # At this point we know that the model instance has been saved into the db.
    from .fields import GalleryField
    fields = [field for field in sender._meta.fields
              if type(field) in [GalleryField]]

    for field in fields:
        old_value_attr = conf.OLD_VALUE_STR % field.name
        deleted_value_attr = conf.DELETED_VALUE_STR % field.name
        if not hasattr(instance, old_value_attr):
            continue

        old_images = (getattr(instance, old_value_attr) or [])
        if isinstance(old_images, str):
            old_images = json.loads(old_images) or []

        assert isinstance(old_images, list)

        current_images = getattr(instance, field.name)
        assert isinstance(current_images, str)

        current_images = json.loads(current_images) or []

        assert isinstance(current_images, list)

        deleted_images = getattr(instance, deleted_value_attr) or []
        if isinstance(deleted_images, str):
            deleted_images = json.loads(deleted_images) or []

        assert isinstance(deleted_images, list)

        new_images = []
        changed = False

        for img in current_images:
            new_images.append(img)

        for img in deleted_images:
            # todo remove those img
            pass

        for img in old_images:
            if img not in current_images and img not in deleted_images:
                changed = True
                new_images.append(img)

        delattr(instance, old_value_attr)
        delattr(instance, deleted_value_attr)

        if changed:
            setattr(instance, field.name, json.dumps(new_images))
            instance.save()
