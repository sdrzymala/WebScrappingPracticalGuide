namespace WebScrapingPudelekPL.Migrations
{
    using System;
    using System.Data.Entity.Migrations;
    
    public partial class Initial : DbMigration
    {
        public override void Up()
        {
            CreateTable(
                "dbo.Articles",
                c => new
                    {
                        Id = c.Int(nullable: false, identity: true),
                        Url = c.String(),
                        Title = c.String(),
                        CreatedAt = c.DateTime(nullable: false),
                        Author = c.String(),
                        Content = c.String(),
                        NumberOfComments = c.Int(nullable: false),
                        NumberOfLikes = c.Int(nullable: false),
                    })
                .PrimaryKey(t => t.Id);
            
            CreateTable(
                "dbo.Comments",
                c => new
                    {
                        Id = c.Int(nullable: false, identity: true),
                        Author = c.Int(nullable: false),
                        CreatedAt = c.Int(nullable: false),
                        Message = c.Int(nullable: false),
                        ThumbsUp = c.Int(nullable: false),
                        ThumbsDown = c.Int(nullable: false),
                        IsHighlited = c.Int(nullable: false),
                        Article_Id = c.Int(),
                    })
                .PrimaryKey(t => t.Id)
                .ForeignKey("dbo.Articles", t => t.Article_Id)
                .Index(t => t.Article_Id);
            
            CreateTable(
                "dbo.Tags",
                c => new
                    {
                        Id = c.Int(nullable: false, identity: true),
                        TagName = c.String(),
                        Article_Id = c.Int(),
                    })
                .PrimaryKey(t => t.Id)
                .ForeignKey("dbo.Articles", t => t.Article_Id)
                .Index(t => t.Article_Id);
            
        }
        
        public override void Down()
        {
            DropForeignKey("dbo.Tags", "Article_Id", "dbo.Articles");
            DropForeignKey("dbo.Comments", "Article_Id", "dbo.Articles");
            DropIndex("dbo.Tags", new[] { "Article_Id" });
            DropIndex("dbo.Comments", new[] { "Article_Id" });
            DropTable("dbo.Tags");
            DropTable("dbo.Comments");
            DropTable("dbo.Articles");
        }
    }
}
