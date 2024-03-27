-- --------------------------------------------------------
-- Host:                         mysql.luomus.fi
-- Server version:               10.5.22-MariaDB - MariaDB Server
-- Server OS:                    Linux
-- HeidiSQL Version:             11.3.0.6295
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Dumping structure for table mammalbase.mb_table_dietsetitem_data
CREATE TABLE IF NOT EXISTS `mb_table_dietsetitem_data` (
  `diet_set_id` int(11) NOT NULL,
  `dsi_id` int(11) NOT NULL DEFAULT 0,
  `tsn` bigint(11) NOT NULL DEFAULT 0,
  `list_order` smallint(5) unsigned NOT NULL,
  `n_food_item` bigint(21) DEFAULT NULL,
  `food_item_percentage` decimal(27,4) DEFAULT NULL,
  `cp_std` decimal(11,7) DEFAULT NULL,
  `ee_std` decimal(11,7) DEFAULT NULL,
  `cf_std` decimal(11,7) DEFAULT NULL,
  `ash_std` decimal(11,7) DEFAULT NULL,
  `nfe_std` decimal(11,7) DEFAULT NULL,
  KEY `diet_set_id` (`diet_set_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table mammalbase.mb_table_dietset_data
CREATE TABLE IF NOT EXISTS `mb_table_dietset_data` (
  `id` int(11) NOT NULL DEFAULT 0,
  `ds_id` int(11) NOT NULL DEFAULT 0,
  `n_ds` bigint(21) DEFAULT NULL,
  `n_months` decimal(27,0) DEFAULT NULL,
  `time_in_months` decimal(5,0) NOT NULL DEFAULT 0,
  `n_food_item` bigint(21) DEFAULT NULL,
  KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table mammalbase.mb_table_master_trait_values
CREATE TABLE IF NOT EXISTS `mb_table_master_trait_values` (
  `id` int(11) DEFAULT NULL,
  `master_id` int(11) DEFAULT NULL,
  `master_entity_name` varchar(250) DEFAULT NULL,
  `master_attribute_id` int(11) DEFAULT NULL,
  `master_attribute_name` varchar(250) DEFAULT NULL,
  `traits_references` mediumtext DEFAULT NULL,
  `assigned_values` mediumtext DEFAULT NULL,
  `n_distinct_value` int(11) DEFAULT NULL,
  `n_value` int(11) DEFAULT NULL,
  `n_supporting_value` int(11) DEFAULT NULL,
  `trait_values` mediumtext DEFAULT NULL,
  `trait_selected` mediumtext DEFAULT NULL,
  `trait_references` mediumtext DEFAULT NULL,
  `value_percentage` decimal(24,4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
