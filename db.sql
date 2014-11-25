-- phpMyAdmin SQL Dump
-- version 3.4.10.1deb1
-- http://www.phpmyadmin.net
--
-- 主机: localhost
-- 生成日期: 2013 年 10 月 24 日 12:05
-- 服务器版本: 5.5.32
-- PHP 版本: 5.3.10-1ubuntu3.8

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- 数据库: `spider`
--

-- --------------------------------------------------------

--
-- 表的结构 `domain`
--

CREATE TABLE IF NOT EXISTS `domain` (
  `domain` varchar(50) NOT NULL,
  `domain_name` varchar(50) NOT NULL,
  `maxurls` int(10) NOT NULL,
  `status` varchar(10) NOT NULL,
  PRIMARY KEY (`domain`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- 转存表中的数据 `domain`
--

INSERT INTO `domain` (`domain`, `domain_name`, `maxurls`, `status`) VALUES
('51auto.com', '51汽车网', 1000, '抓取中');

-- --------------------------------------------------------

--
-- 表的结构 `flow`
--

CREATE TABLE IF NOT EXISTS `flow` (
  `domain` varchar(50) NOT NULL,
  `flow` varchar(50) NOT NULL,
  `list_page_xpath` varchar(100) NOT NULL,
  `list_page_regex` varchar(100) NOT NULL,
  `detail_page_xpath` varchar(100) NOT NULL,
  `detail_page_regex` varchar(100) NOT NULL,
  `seeds` varchar(1000) NOT NULL,
  `interval` int(8) NOT NULL,
  `enabled` int(2) NOT NULL,
  `weight` int(3) NOT NULL,
  `priority` int(3) NOT NULL,
  PRIMARY KEY (`flow`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- 转存表中的数据 `flow`
--

INSERT INTO `flow` (`domain`, `flow`, `list_page_xpath`, `list_page_regex`, `detail_page_xpath`, `detail_page_regex`, `seeds`, `interval`, `enabled`, `weight`, `priority`) VALUES
('51auto.com', '51auto_all', '//div[@class=''fenye_new'']/ul/li/a[contains(text(), ''下一页'')]/@href', '.*/quanguo/search/\\?offset=10&page=\\d+', '//div[@class=''sr_carcn'']/strong/a/@href', '.*/buycar/\\d+\\.html', '["http://www.51auto.com/quanguo/search/"]', 3600, 1, 10, 1);

-- --------------------------------------------------------

--
-- 表的结构 `rule`
--

CREATE TABLE IF NOT EXISTS `rule` (
  `domain` varchar(20) NOT NULL,
  `car_title` varchar(200) NOT NULL,
  `car_brand` varchar(200) NOT NULL,
  `car_series` varchar(200) NOT NULL,
  `car_style` varchar(200) NOT NULL,
  `car_type` varchar(200) NOT NULL,
  `car_publish_logo` varchar(200) NOT NULL,
  `car_emission` varchar(200) NOT NULL,
  `car_transmission` varchar(200) NOT NULL,
  `car_outer_color` varchar(200) NOT NULL,
  `car_inner_color` varchar(200) NOT NULL,
  `car_age` varchar(200) NOT NULL,
  `car_enter_time` varchar(200) NOT NULL,
  `car_images` varchar(200) NOT NULL,
  `car_description` varchar(200) NOT NULL,
  `car_mileage` varchar(200) NOT NULL,
  `car_price` varchar(200) NOT NULL,
  `purchase_price_refer` varchar(200) NOT NULL,
  `source_province` varchar(200) NOT NULL,
  `source_zone` varchar(200) NOT NULL,
  `source_birth` varchar(200) NOT NULL,
  `contact` varchar(200) NOT NULL,
  `car_broker` varchar(200) NOT NULL,
  `contact_phone` varchar(200) NOT NULL,
  `contact_mobile` varchar(200) NOT NULL,
  `contact_addr` varchar(200) NOT NULL,
  `car_invoice` varchar(200) NOT NULL,
  `car_surcharge` varchar(200) NOT NULL,
  `car_tax_valid` varchar(200) NOT NULL,
  `car_insur_validity` varchar(200) NOT NULL,
  `car_inspection_date` varchar(200) NOT NULL,
  `car_license_at` varchar(200) NOT NULL,
  `car_transfer_times` varchar(200) NOT NULL,
  `car_transaction_loc` varchar(200) NOT NULL,
  `car_birth` varchar(200) NOT NULL,
  `car_usage` varchar(200) NOT NULL,
  `car_care` varchar(200) NOT NULL,
  PRIMARY KEY (`domain`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- 转存表中的数据 `rule`
--

INSERT INTO `rule` (`domain`, `car_title`, `car_brand`, `car_series`, `car_style`, `car_type`, `car_publish_logo`, `car_emission`, `car_transmission`, `car_outer_color`, `car_inner_color`, `car_age`, `car_enter_time`, `car_images`, `car_description`, `car_mileage`, `car_price`, `purchase_price_refer`, `source_province`, `source_zone`, `source_birth`, `contact`, `car_broker`, `contact_phone`, `contact_mobile`, `contact_addr`, `car_invoice`, `car_surcharge`, `car_tax_valid`, `car_insur_validity`, `car_inspection_date`, `car_license_at`, `car_transfer_times`, `car_transaction_loc`, `car_birth`, `car_usage`, `car_care`) VALUES
('51auto.com', '//div[@class=''ocar_imp'']/h1/text()#.*', '//td[text()=''品牌'']/following-sibling::td[1]//text()#.*', '//div[@class=''daohang'']/a[4]/text()#二手(.*)', '', '//div[@class=''ocar_imp'']/h1/text()#【.*】 (.*)', '', '//td[text()=''品牌'']/following-sibling::b[1]//text()#.*', '//dl[@class=''or_dl'']/dd[2]/p[2]/text()#.*', '//dl[@class=''or_dl'']/dd[3]/p[1]/text()#(.*)/.*', '//dl[@class=''or_dl'']/dd[3]/p[1]/text()#.*/(.*)', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '//ul[@class=''order_meg'']/li[2]/text()#.*', '', '', '', '');

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
