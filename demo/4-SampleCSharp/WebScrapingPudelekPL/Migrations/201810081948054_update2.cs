namespace WebScrapingPudelekPL.Migrations
{
    using System;
    using System.Data.Entity.Migrations;
    
    public partial class update2 : DbMigration
    {
        public override void Up()
        {
            AlterColumn("dbo.Articles", "CreatedAt", c => c.DateTime());
            AlterColumn("dbo.Articles", "NumberOfComments", c => c.Int());
            AlterColumn("dbo.Articles", "NumberOfLikes", c => c.Int());
            AlterColumn("dbo.Comments", "Author", c => c.String());
            AlterColumn("dbo.Comments", "CreatedAt", c => c.DateTime());
            AlterColumn("dbo.Comments", "Message", c => c.String());
            AlterColumn("dbo.Comments", "ThumbsUp", c => c.Int());
            AlterColumn("dbo.Comments", "ThumbsDown", c => c.Int());
            AlterColumn("dbo.Comments", "IsHighlited", c => c.Boolean());
        }
        
        public override void Down()
        {
            AlterColumn("dbo.Comments", "IsHighlited", c => c.Int(nullable: false));
            AlterColumn("dbo.Comments", "ThumbsDown", c => c.Int(nullable: false));
            AlterColumn("dbo.Comments", "ThumbsUp", c => c.Int(nullable: false));
            AlterColumn("dbo.Comments", "Message", c => c.Int(nullable: false));
            AlterColumn("dbo.Comments", "CreatedAt", c => c.Int(nullable: false));
            AlterColumn("dbo.Comments", "Author", c => c.Int(nullable: false));
            AlterColumn("dbo.Articles", "NumberOfLikes", c => c.Int(nullable: false));
            AlterColumn("dbo.Articles", "NumberOfComments", c => c.Int(nullable: false));
            AlterColumn("dbo.Articles", "CreatedAt", c => c.DateTime(nullable: false));
        }
    }
}
