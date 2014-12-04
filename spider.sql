-- phpMyAdmin SQL Dump
-- version 4.0.10deb1
-- http://www.phpmyadmin.net
--
-- 主机: localhost
-- 生成日期: 2014-12-04 08:23:48
-- 服务器版本: 5.5.40-0ubuntu0.14.04.1
-- PHP 版本: 5.5.9-1ubuntu4.5

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- 数据库: `spider`
--
CREATE DATABASE IF NOT EXISTS `spider` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `spider`;

-- --------------------------------------------------------

--
-- 表的结构 `domain`
--

CREATE TABLE IF NOT EXISTS `domain` (
  `domain` varchar(50) NOT NULL COMMENT '域名',
  `domain_name` varchar(50) NOT NULL COMMENT '域名别名',
  `maxurls` int(10) NOT NULL DEFAULT '300' COMMENT '最大调度链接数',
  `download_delay` float NOT NULL DEFAULT '0' COMMENT '下载延迟',
  `concurrent_requests` int(4) NOT NULL DEFAULT '16' COMMENT '并行数',
  `status` int(1) NOT NULL DEFAULT '0' COMMENT '状态',
  PRIMARY KEY (`domain`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- 转存表中的数据 `domain`
--

INSERT INTO `domain` (`domain`, `domain_name`, `maxurls`, `download_delay`, `concurrent_requests`, `status`) VALUES
('51auto.com', '51汽车网', 1000, 0, 16, 1);

-- --------------------------------------------------------

--
-- 表的结构 `flow`
--

CREATE TABLE IF NOT EXISTS `flow` (
  `domain` varchar(50) NOT NULL COMMENT '域名',
  `flow` varchar(50) NOT NULL COMMENT '流',
  `list_page_xpath` varchar(100) NOT NULL COMMENT '列表页路径',
  `list_page_regex` varchar(100) NOT NULL COMMENT '列表页正则',
  `detail_page_xpath` varchar(100) NOT NULL COMMENT '详细页路径',
  `detail_page_regex` varchar(100) NOT NULL COMMENT '详细页正则',
  `pageno_xpath` varchar(100) NOT NULL COMMENT '页码路径',
  `pageno_regex` varchar(100) NOT NULL DEFAULT '\\d+' COMMENT '页码正则',
  `page_limit` int(5) NOT NULL DEFAULT '0' COMMENT '最大页数',
  `seeds` varchar(1000) NOT NULL DEFAULT '[]' COMMENT '初始链接',
  `interval` int(8) NOT NULL DEFAULT '20' COMMENT '调度单位时间(s)',
  `enabled` int(1) NOT NULL DEFAULT '1' COMMENT '状态',
  `weight` int(3) NOT NULL DEFAULT '1' COMMENT '权重',
  `priority` int(3) NOT NULL DEFAULT '1' COMMENT '优先级',
  PRIMARY KEY (`flow`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- 转存表中的数据 `flow`
--

INSERT INTO `flow` (`domain`, `flow`, `list_page_xpath`, `list_page_regex`, `detail_page_xpath`, `detail_page_regex`, `pageno_xpath`, `pageno_regex`, `page_limit`, `seeds`, `interval`, `enabled`, `weight`, `priority`) VALUES
('51auto.com', '51auto_all', '//div[@class=''fenye_new'']/ul/li/a[contains(text(), ''下一页'')]/@href', '.*/quanguo/search/\\?page=\\d+', '//div[@class=''sr_cl'']//strong/a/@href', '.*/buycar/\\d+\\.html', '//span[@class=''ona'']/text()', '\\d+', 0, '["http://www.51auto.com/quanguo/search/"]', 21600, 1, 10, 1);

-- --------------------------------------------------------

--
-- 表的结构 `rule`
--

CREATE TABLE IF NOT EXISTS `rule` (
  `domain` varchar(20) NOT NULL COMMENT '域名',
  `car_title` varchar(200) NOT NULL COMMENT '标题',
  `car_brand` varchar(200) NOT NULL COMMENT '品牌',
  `car_series` varchar(200) NOT NULL COMMENT '车系',
  `car_style` varchar(200) NOT NULL COMMENT '车身类型',
  `car_type` varchar(200) NOT NULL COMMENT '车型',
  `car_publish_logo` varchar(200) NOT NULL COMMENT '年款',
  `car_emission` varchar(200) NOT NULL COMMENT '排量(L)',
  `car_transmission` varchar(200) NOT NULL COMMENT '变速箱类型',
  `car_outer_color` varchar(200) NOT NULL COMMENT '车身颜色',
  `car_inner_color` varchar(200) NOT NULL COMMENT '内饰颜色',
  `car_age` varchar(200) NOT NULL COMMENT '车龄',
  `car_enter_time` varchar(200) NOT NULL COMMENT '首次上牌日期',
  `car_images` varchar(200) NOT NULL COMMENT '图片',
  `car_description` varchar(200) NOT NULL COMMENT '描述',
  `car_mileage` varchar(200) NOT NULL COMMENT '里程数',
  `car_price` varchar(200) NOT NULL COMMENT '报价',
  `purchase_price_refer` varchar(200) NOT NULL COMMENT '新车指导价',
  `source_province` varchar(200) NOT NULL COMMENT '省份',
  `source_zone` varchar(200) NOT NULL COMMENT '地区',
  `source_birth` varchar(200) NOT NULL COMMENT '发布时间',
  `contact` varchar(200) NOT NULL COMMENT '联系人',
  `car_broker` varchar(200) NOT NULL COMMENT '经销商',
  `contact_phone` varchar(200) NOT NULL COMMENT '联系电话(固)',
  `contact_mobile` varchar(200) NOT NULL COMMENT '联系电话(移)',
  `contact_addr` varchar(200) NOT NULL COMMENT '联系地址',
  `car_invoice` varchar(200) NOT NULL COMMENT '购车发票',
  `car_surcharge` varchar(200) NOT NULL COMMENT '购置税',
  `car_tax_valid` varchar(200) NOT NULL COMMENT '车船使用税',
  `car_insur_validity` varchar(200) NOT NULL COMMENT '保险到期时间',
  `car_inspection_date` varchar(200) NOT NULL COMMENT '上次年检时间',
  `car_license_at` varchar(200) NOT NULL COMMENT '牌照所在地',
  `car_transfer_times` varchar(200) NOT NULL COMMENT '转手次数',
  `car_transaction_loc` varchar(200) NOT NULL COMMENT '交易地点',
  `car_birth` varchar(200) NOT NULL COMMENT '出产年月',
  `car_usage` varchar(200) NOT NULL COMMENT '车辆用途',
  `car_care` varchar(200) NOT NULL COMMENT '保养情况',
  PRIMARY KEY (`domain`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- 转存表中的数据 `rule`
--

INSERT INTO `rule` (`domain`, `car_title`, `car_brand`, `car_series`, `car_style`, `car_type`, `car_publish_logo`, `car_emission`, `car_transmission`, `car_outer_color`, `car_inner_color`, `car_age`, `car_enter_time`, `car_images`, `car_description`, `car_mileage`, `car_price`, `purchase_price_refer`, `source_province`, `source_zone`, `source_birth`, `contact`, `car_broker`, `contact_phone`, `contact_mobile`, `contact_addr`, `car_invoice`, `car_surcharge`, `car_tax_valid`, `car_insur_validity`, `car_inspection_date`, `car_license_at`, `car_transfer_times`, `car_transaction_loc`, `car_birth`, `car_usage`, `car_care`) VALUES
('51auto.com', 'xpath##//div[@class=''otop_div'']/h1/b/text()#.*', 'xpath##//td[text()=''厂商'']/following-sibling::td[1]/text()#.*', 'xpath##//div[@class=''daohang'']/a[4]/text()#二手(.*)', 'xpath##//td[text()=''车体结构'']/following-sibling::td[1]/text()#.*', 'xpath##//div[@class=''daohang'']/a[position()=last()]/h1/text()#.*', 'xpath##//td[text()=''年款'']/following-sibling::td[1]/text()#.*', 'xpath##//td[text()=''排量（L）'']/following-sibling::td[1]/text()#.*', 'xpath##//td[text()=''简称'']/following-sibling::td[1]/text()#.*', 'xpath##//dd/p/i[text()=''车身颜色：'']/following-sibling::text()#(.*)/.*', 'xpath##//dd/p/i[text()=''车身颜色：'']/following-sibling::text()#.*/(.*)', 'xpath##//dd/p/i[text()=''首次上牌：'']/following-sibling::text()#.*\\((\\d+)年\\)', 'xpath##//dd/p/i[text()=''首次上牌：'']/following-sibling::text()#(.*)\\(\\d+年\\)', 'xpath##//ul[@class=''bigpic_ul'']/li/a/@href#.*', 'xpath##//p[@class=''o_pmain'']/text()#.*', 'xpath##//dd/p/i[text()=''行驶里程：'']/following-sibling::text()#(.*)公里', 'xpath##//dt//span[@class=''oyellow1'']/text()#.*', 'xpath##//dt//i[@class=''d_nof'']/following-sibling::strong/text()#(.*)\\+.*', 'xpath##//div[@class=''otop_div'']/h1/b/text()#【(.*)】.*', 'xpath##//div[@class=''otop_div'']/h1/b/text()#【(.*)】.*', 'fr###frequest_51auto###regex##var s5="(.*)";s0\\[4\\]=s5;', 'xpath##//dd/span[starts-with(text(), ''联'')]/following-sibling::text()#.*', 'xpath##//dl[@class=''sm_dl'']/dt/span/a[@class=''a_ktit'']/text()#.*', 'xpath##//div[@class=''ophone_height'']/img/@src#.*', 'xpath##//div[@class=''ophone_height'']/img/@src#.*', 'xpath##//p[@class=''lookcar'']/i/text()#.*', 'xpath##//ul/li/i[text()=''购车/过户发票：'']/../text()#.*', 'xpath##//ul/li/i[text()=''购置税：'']/../text()#.*', 'xpath##//ul/li/i[text()=''车船使用税有效期：'']/../text()#.*', 'xpath##//ul/li/i[text()=''交强险截止日期：'']/../text()#.*', 'xpath##//ul/li/i[text()=''车辆年审日期：'']/../text()#.*', '', '', '', '', 'xpath##//ul/li/i[text()=''车辆用途：'']/../text()#.*', 'xpath##//ul/li/i[text()=''维修保养记录：'']/../text()#.*');

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
