-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 21, 2026 at 12:36 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `workxtrackr`
--

-- --------------------------------------------------------

--
-- Table structure for table `announcements`
--

CREATE TABLE `announcements` (
  `id` int(11) NOT NULL,
  `title` varchar(200) DEFAULT NULL,
  `content` text DEFAULT NULL,
  `announcement_date` date DEFAULT NULL,
  `created_date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `announcements`
--

INSERT INTO `announcements` (`id`, `title`, `content`, `announcement_date`, `created_date`) VALUES
(5, 'meetings', 'mag meetings ta guys', '2026-01-28', '2026-01-28'),
(6, 'exhibitions', 'tara', '2026-01-28', '2026-01-28'),
(7, 'reminders', 'pa remind lang nako', '2026-01-28', '2026-01-28'),
(8, 'New product launches', 'let\'s Go!', '2026-01-28', '2026-01-28'),
(9, 'Birth Day Celebration', 'Mag pa kaon ko', '2026-01-28', '2026-01-28'),
(10, 'Parties', 'mag party ta kay kapuy trabaho', '2026-01-31', '2026-01-28'),
(11, 'weddings', 'mag attend tag wedding ceremony', '2026-02-06', '2026-01-28'),
(12, 'policy changes', 'new policy changesin our company', '2026-01-28', '2026-01-28');

-- --------------------------------------------------------

--
-- Table structure for table `attendance`
--

CREATE TABLE `attendance` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `clock_in` time DEFAULT NULL,
  `clock_out` time DEFAULT NULL,
  `status` varchar(20) DEFAULT 'absent',
  `late_minutes` int(11) DEFAULT 0,
  `overtime_minutes` int(11) DEFAULT 0,
  `total_hours` decimal(5,2) DEFAULT 0.00,
  `duration_hours` decimal(5,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `attendance`
--

INSERT INTO `attendance` (`id`, `user_id`, `date`, `clock_in`, `clock_out`, `status`, `late_minutes`, `overtime_minutes`, `total_hours`, `duration_hours`) VALUES
(68, 2, '2026-01-19', '14:31:53', '14:31:56', 'late', 316, 0, 0.00, 0.00),
(69, 4, '2026-01-19', '14:32:11', '14:32:13', 'late', 317, 0, 0.00, 0.00),
(70, 2, '2026-01-20', '15:50:52', '15:50:54', 'late', 395, 0, 0.00, 0.00),
(71, 2, '2026-01-24', '17:20:03', '17:20:05', 'late', 485, 20, 0.00, 0.00),
(72, 2, '2026-01-26', '18:45:41', '18:45:43', 'late', 570, 105, 0.00, 0.00),
(73, 4, '2026-01-26', '18:46:04', '18:46:06', 'late', 571, 106, 0.00, 0.00),
(74, 3, '2026-01-26', '18:46:37', '18:46:39', 'late', 571, 106, 0.00, 0.00),
(75, 2, '2026-01-26', '22:54:35', '22:54:37', 'late', 819, 354, 0.00, 0.00),
(76, 2, '2026-01-27', '00:40:03', '00:40:05', 'present', 0, 0, 0.00, 0.00),
(77, 2, '2026-01-27', '01:04:05', '01:04:07', 'present', 0, 0, 0.00, 0.00),
(78, 2, '2026-01-27', '13:30:43', '13:30:47', 'late', 255, 0, 0.00, 0.00),
(79, 2, '2026-01-27', '21:10:47', '21:10:50', 'late', 715, 250, 0.00, 0.00),
(80, 2, '2026-01-28', '10:24:46', '10:24:50', 'late', 69, 0, 0.00, 0.00),
(81, 4, '2026-01-28', '10:25:00', '10:25:02', 'late', 70, 0, 0.00, 0.00),
(82, 3, '2026-01-28', '10:25:12', '10:25:13', 'late', 70, 0, 0.00, 0.00),
(83, 7, '2026-01-28', '10:25:26', '10:25:28', 'late', 70, 0, 0.00, 0.00),
(84, 2, '2026-01-28', '18:15:29', '18:15:31', 'late', 540, 75, 0.00, 0.00),
(85, 2, '2026-02-06', '15:57:16', '15:57:31', 'late', 402, 0, 0.00, 0.00),
(86, 4, '2026-02-06', '16:26:52', '16:26:55', 'late', 431, 0, 0.00, 0.00),
(87, 3, '2026-02-06', '16:33:56', '16:33:58', 'late', 438, 0, 0.00, 0.00),
(88, 7, '2026-02-06', '16:34:30', '16:34:32', 'late', 439, 0, 0.00, 0.00),
(89, 8, '2026-02-06', '16:36:25', '16:36:27', 'late', 441, 0, 0.00, 0.00),
(90, 2, '2026-02-08', '11:00:09', '11:00:13', 'late', 105, 0, 0.00, 0.00),
(91, 7, '2026-02-08', '11:01:11', '11:01:15', 'late', 106, 0, 0.00, 0.00),
(92, 8, '2026-02-08', '11:01:32', NULL, 'late', 0, 0, 0.00, NULL),
(93, 4, '2026-02-08', '11:02:38', NULL, 'late', 0, 0, 0.00, NULL),
(94, 2, '2026-02-09', '13:01:26', '13:01:29', 'late', 226, 0, 0.00, 0.00),
(95, 7, '2026-02-09', '13:01:43', '13:01:45', 'late', 226, 0, 0.00, 0.00),
(96, 4, '2026-02-09', '13:02:00', '13:02:03', 'late', 227, 0, 0.00, 0.00),
(97, 2, '2026-02-09', '13:06:21', '13:06:39', 'late', 231, 0, 0.01, 0.01),
(98, 2, '2026-02-10', '14:15:19', '14:15:25', 'late', 300, 0, 0.00, 0.00),
(99, 2, '2026-02-10', '14:19:55', NULL, 'late', 0, 0, 0.00, NULL),
(100, 2, '2026-02-15', '09:43:21', '09:43:24', 'late', 28, 0, 0.00, 0.00),
(101, 4, '2026-02-15', '10:02:46', '10:02:48', 'late', 47, 0, 0.00, 0.00),
(103, 3, '2026-02-15', '10:33:26', '10:33:28', 'late', 78, 0, 0.00, 0.00),
(104, 7, '2026-02-15', '11:09:21', '11:09:25', 'late', 114, 0, 0.00, 0.00),
(105, 10, '2026-02-15', '13:17:56', '13:17:58', 'late', 242, 0, 0.00, 0.00),
(106, 4, '2026-02-17', '14:21:16', '14:21:19', 'late', 306, 0, 0.00, 0.00),
(107, 3, '2026-02-17', '14:25:36', '14:25:38', 'late', 310, 0, 0.00, 0.00),
(108, 7, '2026-02-17', '14:25:50', '14:25:53', 'late', 310, 0, 0.00, 0.00),
(109, 10, '2026-02-17', '14:26:16', '14:26:17', 'late', 311, 0, 0.00, 0.00),
(110, 9, '2026-02-17', '14:26:29', '14:26:30', 'late', 311, 0, 0.00, 0.00),
(111, 2, '2026-02-19', '13:39:59', '13:40:02', 'late', 264, 0, 0.00, 0.00),
(112, 10, '2026-02-19', '13:40:28', '13:40:31', 'late', 265, 0, 0.00, 0.00);

-- --------------------------------------------------------

--
-- Table structure for table `requests`
--

CREATE TABLE `requests` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `request_type` varchar(50) DEFAULT NULL,
  `request_date` date DEFAULT NULL,
  `reason` text DEFAULT NULL,
  `status` varchar(20) DEFAULT 'pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `requests`
--

INSERT INTO `requests` (`id`, `user_id`, `request_type`, `request_date`, `reason`, `status`, `created_at`) VALUES
(19, 2, 'Sick Leave', '2025-12-19', 'Sick Leave ko Sir Thank you', 'approved', '2025-12-19 06:30:25'),
(20, 2, 'Sick Leave', '2025-12-19', 'Sick Leave ko Sir Thank you', 'approved', '2025-12-19 06:54:16'),
(21, 2, 'Vacation Leave', '2025-12-19', 'Sir Mag Vacation sako ha Thank you', 'approved', '2025-12-19 09:11:06'),
(22, 2, 'Emergency Leave', '2025-12-19', 'Sir Emergency Thank you', 'approved', '2025-12-19 11:11:31'),
(23, 2, 'Equipment Request', '2026-01-02', 'Sir Request kog Iphone 17 pro max 1000', 'declined', '2025-12-19 11:20:54'),
(24, 2, 'Vacation Leave', '2026-01-26', 'Mag Vacation ko sir ha thank you', 'approved', '2026-01-26 10:47:22'),
(25, 2, 'Sick Leave', '2026-01-27', 'Sick Leave ko sir kamatyunon nako', 'declined', '2026-01-27 05:31:19'),
(26, 2, 'Vacation Leave', '2026-01-28', 'Maligo sa ko ug dagat sir', 'approved', '2026-01-28 01:10:15'),
(27, 2, 'Vacation Leave', '2026-02-09', 'Maligo kog dagat sir', 'pending', '2026-02-08 03:00:04'),
(28, 7, 'Training/Seminar', '2026-02-10', 'mag seminar ko ana nga date sir', 'pending', '2026-02-08 03:01:05'),
(29, 8, 'Emergency Leave', '2026-02-08', 'nasunog akong giluto na hotdog sir, Emergency ni', 'pending', '2026-02-08 03:02:07'),
(30, 4, 'Vacation Leave', '2026-02-10', 'sir mag vacation ko', 'pending', '2026-02-08 03:03:17');

-- --------------------------------------------------------

--
-- Table structure for table `system_config`
--

CREATE TABLE `system_config` (
  `id` int(11) NOT NULL,
  `config_type` varchar(50) NOT NULL DEFAULT 'work_time',
  `work_start_time` time DEFAULT '09:00:00',
  `work_end_time` time DEFAULT '17:00:00',
  `grace_period_minutes` int(11) DEFAULT 15,
  `overtime_threshold_hours` int(11) DEFAULT 8,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `system_config`
--

INSERT INTO `system_config` (`id`, `config_type`, `work_start_time`, `work_end_time`, `grace_period_minutes`, `overtime_threshold_hours`, `created_at`, `updated_at`) VALUES
(1, 'work_time', '08:00:00', '17:00:00', 15, 5, '2026-01-24 11:28:15', '2026-02-15 02:34:51');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `role` varchar(20) DEFAULT 'staff'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `full_name`, `email`, `role`) VALUES
(1, 'admin', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'Super Admin', 'admin@email.com', 'admin'),
(2, 'dannbucao', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'Theo Bucao', 'dannbucao@gmail.com', 'staff'),
(3, 'lambert', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'Lambert Fernando', 'LambertFernando@gmail.com', 'staff'),
(4, 'alicaya', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'Levi Alicaya', 'Alicaya@gmail.com', 'staff'),
(5, 'ashton', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'Ashton Dormille', 'ashton@gmail.com', 'staff'),
(7, 'staff1', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'staffnumber1', 'staff1@gmail.com', 'staff'),
(8, 'staff2', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'staffnumber2', 'staff2@gmail.com', 'staff'),
(9, 'staff3', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'staffnumber3', 'staff3@gmail.com', 'staff'),
(10, 'staff4', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'staffnumber4', 'staff4@gmail.com', 'staff');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `announcements`
--
ALTER TABLE `announcements`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `attendance`
--
ALTER TABLE `attendance`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_attendance_user_date` (`user_id`,`date`),
  ADD KEY `idx_attendance_date` (`date`);

--
-- Indexes for table `requests`
--
ALTER TABLE `requests`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `system_config`
--
ALTER TABLE `system_config`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_config_type` (`config_type`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `announcements`
--
ALTER TABLE `announcements`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `attendance`
--
ALTER TABLE `attendance`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=113;

--
-- AUTO_INCREMENT for table `requests`
--
ALTER TABLE `requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT for table `system_config`
--
ALTER TABLE `system_config`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `attendance`
--
ALTER TABLE `attendance`
  ADD CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `requests`
--
ALTER TABLE `requests`
  ADD CONSTRAINT `requests_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
