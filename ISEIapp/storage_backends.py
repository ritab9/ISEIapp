from storages.backends.s3boto3 import S3Boto3Storage

#print("📦 storage_backends module imported")

class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False

    #def _save(self, name, content):
    #    print(f"🧪 Saving file {name} via MediaStorage")
    #    return super()._save(name, content)
