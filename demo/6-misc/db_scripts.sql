USE [master]
GO
/****** Object:  Database [pudelek2]    Script Date: 10/4/2020 8:36:57 PM ******/
CREATE DATABASE [pudelek2]
 CONTAINMENT = NONE
 ON  PRIMARY 
( NAME = N'pudelek2', FILENAME = N'/var/opt/mssql/data/pudelek2.mdf' , SIZE = 204800KB , MAXSIZE = UNLIMITED, FILEGROWTH = 65536KB )
 LOG ON 
( NAME = N'pudelek2_log', FILENAME = N'/var/opt/mssql/data/pudelek2_log.ldf' , SIZE = 204800KB , MAXSIZE = 2048GB , FILEGROWTH = 65536KB )
GO
ALTER DATABASE [pudelek2] SET COMPATIBILITY_LEVEL = 140
GO
IF (1 = FULLTEXTSERVICEPROPERTY('IsFullTextInstalled'))
begin
EXEC [pudelek2].[dbo].[sp_fulltext_database] @action = 'enable'
end
GO
ALTER DATABASE [pudelek2] SET ANSI_NULL_DEFAULT OFF 
GO
ALTER DATABASE [pudelek2] SET ANSI_NULLS OFF 
GO
ALTER DATABASE [pudelek2] SET ANSI_PADDING OFF 
GO
ALTER DATABASE [pudelek2] SET ANSI_WARNINGS OFF 
GO
ALTER DATABASE [pudelek2] SET ARITHABORT OFF 
GO
ALTER DATABASE [pudelek2] SET AUTO_CLOSE ON 
GO
ALTER DATABASE [pudelek2] SET AUTO_SHRINK OFF 
GO
ALTER DATABASE [pudelek2] SET AUTO_UPDATE_STATISTICS ON 
GO
ALTER DATABASE [pudelek2] SET CURSOR_CLOSE_ON_COMMIT OFF 
GO
ALTER DATABASE [pudelek2] SET CURSOR_DEFAULT  GLOBAL 
GO
ALTER DATABASE [pudelek2] SET CONCAT_NULL_YIELDS_NULL OFF 
GO
ALTER DATABASE [pudelek2] SET NUMERIC_ROUNDABORT OFF 
GO
ALTER DATABASE [pudelek2] SET QUOTED_IDENTIFIER OFF 
GO
ALTER DATABASE [pudelek2] SET RECURSIVE_TRIGGERS OFF 
GO
ALTER DATABASE [pudelek2] SET  ENABLE_BROKER 
GO
ALTER DATABASE [pudelek2] SET AUTO_UPDATE_STATISTICS_ASYNC OFF 
GO
ALTER DATABASE [pudelek2] SET DATE_CORRELATION_OPTIMIZATION OFF 
GO
ALTER DATABASE [pudelek2] SET TRUSTWORTHY OFF 
GO
ALTER DATABASE [pudelek2] SET ALLOW_SNAPSHOT_ISOLATION OFF 
GO
ALTER DATABASE [pudelek2] SET PARAMETERIZATION SIMPLE 
GO
ALTER DATABASE [pudelek2] SET READ_COMMITTED_SNAPSHOT OFF 
GO
ALTER DATABASE [pudelek2] SET HONOR_BROKER_PRIORITY OFF 
GO
ALTER DATABASE [pudelek2] SET RECOVERY FULL 
GO
ALTER DATABASE [pudelek2] SET  MULTI_USER 
GO
ALTER DATABASE [pudelek2] SET PAGE_VERIFY CHECKSUM  
GO
ALTER DATABASE [pudelek2] SET DB_CHAINING OFF 
GO
ALTER DATABASE [pudelek2] SET FILESTREAM( NON_TRANSACTED_ACCESS = OFF ) 
GO
ALTER DATABASE [pudelek2] SET TARGET_RECOVERY_TIME = 60 SECONDS 
GO
ALTER DATABASE [pudelek2] SET DELAYED_DURABILITY = DISABLED 
GO
ALTER DATABASE [pudelek2] SET QUERY_STORE = OFF
GO
USE [pudelek2]
GO
/****** Object:  Table [dbo].[Articles]    Script Date: 10/4/2020 8:36:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Articles](
	[article_id] [int] IDENTITY(1,1) NOT NULL,
	[article_url] [nvarchar](255) NULL,
	[article_type] [nvarchar](255) NULL,
	[article_title] [nvarchar](500) NULL,
	[article_created_at] [datetime] NULL,
	[article_author] [nvarchar](255) NULL,
	[article_content] [nvarchar](max) NULL,
	[article_number_of_comments] [int] NULL,
	[article_number_of_bolded_text] [int] NULL,
	[article_has_slideshow] [bit] NULL,
	[article_number_of_videos] [int] NULL,
	[article_number_of_instagram_posts] [int] NULL,
	[article_number_of_images] [int] NULL,
	[article_is_downloaded] [bit] NULL,
	[article_inserted_at] [datetime] NULL,
	[article_updated_at] [datetime] NULL,
 CONSTRAINT [PK_dbo.Articles] PRIMARY KEY CLUSTERED 
(
	[article_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  View [dbo].[vArticles]    Script Date: 10/4/2020 8:36:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO



CREATE view [dbo].[vArticles]

as

SELECT [article_id]
    ,[article_url]
    ,[article_type]
    ,[article_title]
    ,[article_created_at]
    ,[article_author]
    ,[article_content]
    ,[article_number_of_comments]
    ,[article_number_of_bolded_text]
    ,[article_has_slideshow]
	,[article_has_video] = CONVERT(BIT,IIF([article_number_of_videos] > 0, 1, 0))
    ,[article_number_of_videos]
    ,[article_number_of_instagram_posts]
    ,[article_number_of_images]
    ,[article_is_downloaded]
    ,[article_inserted_at]
    ,[article_updated_at]
FROM [dbo].[Articles]
where [article_is_downloaded] = 1
and article_id <> 1280
and [article_created_at] is not null
and [article_author] is not null

GO
/****** Object:  Table [dbo].[Comments]    Script Date: 10/4/2020 8:36:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Comments](
	[comment_id] [int] IDENTITY(1,1) NOT NULL,
	[article_id] [int] NULL,
	[comment_author] [nvarchar](255) NULL,
	[comment_message] [nvarchar](max) NULL,
	[comment_thumbs_up] [int] NULL,
	[comment_thumbs_down] [int] NULL,
	[comment_is_highlited] [bit] NULL,
 CONSTRAINT [PK_dbo.Comments] PRIMARY KEY CLUSTERED 
(
	[comment_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  View [dbo].[vComments]    Script Date: 10/4/2020 8:36:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO


CREATE view [dbo].[vComments]

as

select 
c.comment_id
,c.article_id
,c.comment_author
,c.comment_message
,c.comment_thumbs_up
,c.comment_thumbs_down
,c.comment_is_highlited
from [dbo].[Comments] c (nolock)
where c.article_id IN
(
	select article_id
	from dbo.varticles 
)
GO
/****** Object:  Table [dbo].[RelatedArticles]    Script Date: 10/4/2020 8:36:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[RelatedArticles](
	[related_article_id] [int] IDENTITY(1,1) NOT NULL,
	[article_id] [int] NULL,
	[related_article_text] [nvarchar](2500) NULL,
	[related_article_url] [nvarchar](2500) NULL,
 CONSTRAINT [PK_dbo.RelatedArticles] PRIMARY KEY CLUSTERED 
(
	[related_article_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  View [dbo].[vRelatedArticles]    Script Date: 10/4/2020 8:36:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

create view [dbo].[vRelatedArticles]

as

select 
ra.related_article_id,
ra.article_id,
ra.related_article_text,
ra.related_article_url
from [dbo].[RelatedArticles] ra (nolock)
where article_id in
(
	select article_id
	from dbo.varticles
)
GO
/****** Object:  Table [dbo].[Tags]    Script Date: 10/4/2020 8:36:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Tags](
	[tag_id] [int] IDENTITY(1,1) NOT NULL,
	[article_id] [int] NULL,
	[tag_text] [nvarchar](255) NULL,
	[tag_url] [nvarchar](255) NULL,
 CONSTRAINT [PK_dbo.Tags] PRIMARY KEY CLUSTERED 
(
	[tag_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  View [dbo].[vTags]    Script Date: 10/4/2020 8:36:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

create view [dbo].[vTags]

as

select 
t.tag_id,
t.article_id,
t.tag_text,
t.tag_url
from [dbo].[Tags] t (nolock)
where article_id in
(
	select article_id
	from dbo.varticles
)
GO
/****** Object:  Table [dbo].[__MigrationHistory]    Script Date: 10/4/2020 8:36:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[__MigrationHistory](
	[MigrationId] [nvarchar](150) NOT NULL,
	[ContextKey] [nvarchar](300) NOT NULL,
	[Model] [varbinary](max) NOT NULL,
	[ProductVersion] [nvarchar](32) NOT NULL,
 CONSTRAINT [PK_dbo.__MigrationHistory] PRIMARY KEY CLUSTERED 
(
	[MigrationId] ASC,
	[ContextKey] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
USE [master]
GO
ALTER DATABASE [pudelek2] SET  READ_WRITE 
GO
