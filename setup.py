from setuptools import setup, find_packages

try:
    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ""

setup(
    name="wpat",
    version="2.0",
    author="Undefined_name",
    license="GPLv3",
    description="WPAT (WP Audit Toolkit) es una herramienta de auditoría de seguridad para WordPress que detecta vulnerabilidades comunes y expone riesgos de manera eficiente.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/undefined-name12/WPAZ",
    packages=find_packages(include=["wpat", "wpat.*"]),
    install_requires=[
        'colorama',
        'requests',
        'beautifulsoup4',
        'tqdm',
        'urllib3'
    ],
    extras_require={
        'gui': [
            'pyqt5',
            'PyQtWebEngine'
        ]
    },
    entry_points={
        'console_scripts': [
            'wpat=wpat.main:main'
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Information Technology',
        'Topic :: Security',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.6',
    include_package_data=True,
    zip_safe=False,
    keywords='wordpress security audit toolkit',
    }
)
