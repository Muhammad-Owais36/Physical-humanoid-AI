// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Introduction',
      items: ['intro', 'physical-ai-overview'],
    },
    {
      type: 'category',
      label: 'Module 1: The Robotic Nervous System (ROS 2)',
      items: [
        'ros2-humanoid/chapter1-introduction',
        'ros2-humanoid/chapter2-advanced-concepts',
        'ros2-humanoid/chapter3-practical-implementation'
      ],
    },
    {
      type: 'category',
      label: 'Module 2: The Digital Twin (Gazebo & Unity)',
      items: [
        'digital-twin/chapter1-introduction',
        'digital-twin/chapter2-advanced-concepts',
        'digital-twin/chapter3-practical-implementation'
      ],
    },
    {
      type: 'category',
      label: 'Module 3: The AI-Robot Brain (NVIDIA Isaac™)',
      items: [
        'ai-brain/chapter1-introduction',
        'ai-brain/chapter2-advanced-concepts',
        'ai-brain/chapter3-practical-implementation'
      ],
    },
    {
      type: 'category',
      label: 'Module 4: Vision-Language-Action (VLA)',
      items: [
        'vla/chapter1-introduction',
        'vla/chapter2-advanced-concepts',
        'vla/chapter3-practical-implementation'
      ],
    },
    {
      type: 'category',
      label: 'Reference',
      items: [
        'reference/glossary',
        'reference/faq',
        'reference/troubleshooting'
      ],
    }
  ],
};

module.exports = sidebars;