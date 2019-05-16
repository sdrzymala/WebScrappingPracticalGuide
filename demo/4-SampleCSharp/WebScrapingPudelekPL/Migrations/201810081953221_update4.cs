namespace WebScrapingPudelekPL.Migrations
{
    using System;
    using System.Data.Entity.Migrations;
    
    public partial class update4 : DbMigration
    {
        public override void Up()
        {
            AlterColumn("dbo.Articles", "Url", c => c.String(maxLength: 255));
            AlterColumn("dbo.Articles", "Title", c => c.String(maxLength: 500));
            AlterColumn("dbo.Articles", "Author", c => c.String(maxLength: 255));
            AlterColumn("dbo.Comments", "Author", c => c.String(maxLength: 255));
            AlterColumn("dbo.Tags", "TagName", c => c.String(maxLength: 255));
        }
        
        public override void Down()
        {
            AlterColumn("dbo.Tags", "TagName", c => c.String());
            AlterColumn("dbo.Comments", "Author", c => c.String());
            AlterColumn("dbo.Articles", "Author", c => c.String());
            AlterColumn("dbo.Articles", "Title", c => c.String());
            AlterColumn("dbo.Articles", "Url", c => c.String());
        }
    }
}
