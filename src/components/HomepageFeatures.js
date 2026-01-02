import React from 'react';
import clsx from 'clsx';
import styles from './HomepageFeatures.module.css';

const FeatureList = [
  {
    title: 'Physical AI & Humanoid Robotics',
    description: (
      <>
        Comprehensive guide to AI Systems in the Physical World, focusing on humanoid robots
        that operate in real-world environments.
      </>
    ),
  },
  {
    title: 'Four Core Modules',
    description: (
      <>
        Learn about the Robotic Nervous System (ROS 2), Digital Twin (Gazebo & Unity),
        AI-Robot Brain (NVIDIA Isaac™), and Vision-Language-Action integration.
      </>
    ),
  },
  {
    title: 'Practical Implementation',
    description: (
      <>
        Real-world examples and capstone projects demonstrating autonomous humanoid
        robots performing object recognition, navigation, and manipulation.
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}