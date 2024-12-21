-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versi server:                 8.0.30 - MySQL Community Server - GPL
-- OS Server:                    Win64
-- HeidiSQL Versi:               12.1.0.6537
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- membuang struktur untuk table platex.plates
CREATE TABLE IF NOT EXISTS `plates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `plate_text` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `detected_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Membuang data untuk tabel platex.plates: ~3 rows (lebih kurang)
DELETE FROM `plates`;
INSERT INTO `plates` (`id`, `plate_text`, `detected_at`) VALUES
	(1, 'PB1234ABC', '2024-12-21 18:29:58'),
	(2, 'B 1234 ABC', '2024-12-21 18:29:58'),
	(3, 'B1234ABC', '2024-12-21 18:30:03');

-- membuang struktur untuk table platex.users
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nama` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Membuang data untuk tabel platex.users: ~2 rows (lebih kurang)
DELETE FROM `users`;
INSERT INTO `users` (`id`, `username`, `password`, `nama`) VALUES
	(1, 'zulfi', 'scrypt:32768:8:1$pA5Gj5VVkR9Fr3BE$00e89d5fdab7ead976d1806faeb7be3efd1527775a046e667a4c4f247a5dca6adba6efd5af368b91c2439b7e2a521607eb76c3a983bf8071b42312d1ec064c48', 'Nur Fadilah Zulfi'),
	(2, 'alif', 'scrypt:32768:8:1$Vi8eUSvtw3XCtTiN$d3fad14ef1cd9c4f97e1214d05db84de3fe6d8deb04b2e00e69d3c175f0178cc034f5d785d35885021245966b71f7e95be930d01cc4ba54314bd7cd29b5d23c9', 'Muhammad Alif');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
