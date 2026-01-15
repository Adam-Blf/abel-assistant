"use client";

import { motion } from "framer-motion";
import { SystemWidget } from "./SystemWidget";
import { WeatherWidget } from "./WeatherWidget";
import { EmailWidget } from "./EmailWidget";
import { CalendarWidget } from "./CalendarWidget";
import { SocialWidget } from "./SocialWidget";
import { QuickActionsWidget } from "./QuickActionsWidget";

export function WidgetGrid() {
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="h-full overflow-y-auto p-6"
    >
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* System Status */}
        <motion.div variants={itemVariants} className="lg:col-span-1">
          <SystemWidget />
        </motion.div>

        {/* Weather */}
        <motion.div variants={itemVariants} className="lg:col-span-1">
          <WeatherWidget />
        </motion.div>

        {/* Quick Actions */}
        <motion.div variants={itemVariants} className="lg:col-span-1">
          <QuickActionsWidget />
        </motion.div>

        {/* Emails */}
        <motion.div variants={itemVariants} className="lg:col-span-1">
          <EmailWidget />
        </motion.div>

        {/* Calendar */}
        <motion.div variants={itemVariants} className="lg:col-span-1">
          <CalendarWidget />
        </motion.div>

        {/* Social */}
        <motion.div variants={itemVariants} className="lg:col-span-1">
          <SocialWidget />
        </motion.div>
      </div>
    </motion.div>
  );
}
