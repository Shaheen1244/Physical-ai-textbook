import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/__docusaurus/debug',
    component: ComponentCreator('/__docusaurus/debug', '5ff'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/config',
    component: ComponentCreator('/__docusaurus/debug/config', '5ba'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/content',
    component: ComponentCreator('/__docusaurus/debug/content', 'a2b'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/globalData',
    component: ComponentCreator('/__docusaurus/debug/globalData', 'c3c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/metadata',
    component: ComponentCreator('/__docusaurus/debug/metadata', '156'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/registry',
    component: ComponentCreator('/__docusaurus/debug/registry', '88c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/routes',
    component: ComponentCreator('/__docusaurus/debug/routes', '000'),
    exact: true
  },
  {
    path: '/auth/github-callback',
    component: ComponentCreator('/auth/github-callback', 'c6e'),
    exact: true
  },
  {
    path: '/auth/login',
    component: ComponentCreator('/auth/login', '134'),
    exact: true
  },
  {
    path: '/auth/signup',
    component: ComponentCreator('/auth/signup', 'e56'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs', '819'),
    routes: [
      {
        path: '/docs',
        component: ComponentCreator('/docs', '047'),
        routes: [
          {
            path: '/docs',
            component: ComponentCreator('/docs', 'd85'),
            routes: [
              {
                path: '/docs/book-rag-setup',
                component: ComponentCreator('/docs/book-rag-setup', '04e'),
                exact: true
              },
              {
                path: '/docs/chapter_1',
                component: ComponentCreator('/docs/chapter_1', '59a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter_10',
                component: ComponentCreator('/docs/chapter_10', '338'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter_11',
                component: ComponentCreator('/docs/chapter_11', '0d4'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter_12',
                component: ComponentCreator('/docs/chapter_12', '616'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter_13',
                component: ComponentCreator('/docs/chapter_13', 'ae8'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter_14',
                component: ComponentCreator('/docs/chapter_14', '6f2'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter_2',
                component: ComponentCreator('/docs/chapter_2', 'f0b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter_3',
                component: ComponentCreator('/docs/chapter_3', '1a0'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter_4',
                component: ComponentCreator('/docs/chapter_4', 'e05'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter_5',
                component: ComponentCreator('/docs/chapter_5', 'c1e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter_6',
                component: ComponentCreator('/docs/chapter_6', '988'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter_7',
                component: ComponentCreator('/docs/chapter_7', 'a12'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter_8',
                component: ComponentCreator('/docs/chapter_8', '795'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter_9',
                component: ComponentCreator('/docs/chapter_9', '8cb'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter-6',
                component: ComponentCreator('/docs/chapter-6', 'b83'),
                exact: true
              },
              {
                path: '/docs/embodied-intelligence',
                component: ComponentCreator('/docs/embodied-intelligence', 'f39'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/gazebo-simulation',
                component: ComponentCreator('/docs/gazebo-simulation', '917'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/intro',
                component: ComponentCreator('/docs/intro', '61d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/isaac-sim',
                component: ComponentCreator('/docs/isaac-sim', '37a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/robotic-manipulation',
                component: ComponentCreator('/docs/robotic-manipulation', 'cb4'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/ros2-fundamentals',
                component: ComponentCreator('/docs/ros2-fundamentals', '1ac'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/synthetic-data-generation',
                component: ComponentCreator('/docs/synthetic-data-generation', '43f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/urdf-xacro-modeling',
                component: ComponentCreator('/docs/urdf-xacro-modeling', '27a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/urdu-intro',
                component: ComponentCreator('/docs/urdu-intro', '1c8'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/urdu-robotics-fundamentals',
                component: ComponentCreator('/docs/urdu-robotics-fundamentals', 'd25'),
                exact: true,
                sidebar: "tutorialSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/',
    component: ComponentCreator('/', '2e1'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
