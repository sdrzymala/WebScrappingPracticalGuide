namespace WebScrapingPudelekPL.Migrations
{
    using System;
    using System.Data.Entity.Migrations;
    
    public partial class update19 : DbMigration
    {
        public override void Up()
        {
            AddColumn("dbo.RelatedArticles", "Text", c => c.String(maxLength: 255));
            AddColumn("dbo.RelatedArticles", "Url", c => c.String(maxLength: 255));
            AddColumn("dbo.Tags", "Text", c => c.String(maxLength: 255));
            AddColumn("dbo.Tags", "Url", c => c.String(maxLength: 255));
            DropColumn("dbo.RelatedArticles", "RelatedText");
            DropColumn("dbo.RelatedArticles", "RelatedName");
            DropColumn("dbo.Tags", "TagText");
            DropColumn("dbo.Tags", "TagUrl");
        }
        
        public override void Down()
        {
            AddColumn("dbo.Tags", "TagUrl", c => c.String(maxLength: 255));
            AddColumn("dbo.Tags", "TagText", c => c.String(maxLength: 255));
            AddColumn("dbo.RelatedArticles", "RelatedName", c => c.String(maxLength: 255));
            AddColumn("dbo.RelatedArticles", "RelatedText", c => c.String(maxLength: 255));
            DropColumn("dbo.Tags", "Url");
            DropColumn("dbo.Tags", "Text");
            DropColumn("dbo.RelatedArticles", "Url");
            DropColumn("dbo.RelatedArticles", "Text");
        }
    }
}
