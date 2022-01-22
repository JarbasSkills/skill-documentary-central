#!/usr/bin/env python3
from setuptools import setup

# skill_id=package_name:SkillClass
PLUGIN_ENTRY_POINT = 'skill-documentary-central.jarbasai=skill_documentary_central:DocumentaryCentralSkill'

setup(
    # this is the package name that goes on pip
    name='ovos-skill-documentary-central',
    version='0.0.1',
    description='ovos classic documentary documentary skill plugin',
    url='https://github.com/JarbasSkills/skill-documentary-central',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    package_dir={"skill_documentary_central": ""},
    package_data={'skill_documentary_central': ['locale/*', 'ui/*']},
    packages=['skill_documentary_central'],
    include_package_data=True,
    install_requires=["ovos_workshop~=0.0.5a1"],
    keywords='ovos skill plugin',
    entry_points={'ovos.plugin.skill': PLUGIN_ENTRY_POINT}
)
