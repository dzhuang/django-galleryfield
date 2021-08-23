import os

from setuptools import find_packages, setup

import galleryfield


def read(fname):
    # file read function copied from sorl.django-documents project
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


install_requires = [
    'sorl-thumbnail',
    'pillow'
]

setup(
    name='django-galleryfield',
    version=galleryfield.__version__,
    description="Django AJAX upload widget and model field for multiple images, featuring drag & drop uploading, upload progress bar, sortable and croppable image gallery",
    long_description_content_type="text/x-rst",
    long_description=read('README.rst'),
    classifiers=[
        # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='django ajax html5 upload widget images gallery sorting crop progress'
             'thumbnails multiple GalleryField admin forms field',
    author='Dong Zhuang',
    author_email='dzhuang.scut@gmail.com',
    url='https://github.com/dzhuang/django-galleryfield',
    license='MIT',
    packages=find_packages(exclude=['tests', 'demo']),
    include_package_data=True,
    zip_safe=True,
    install_requires=install_requires,
    entry_points="""
        # -*- Entry points: -*-
    """,
)
