namespace WebScrapingPudelekPL.Migrations
{
    using System;
    using System.Data.Entity.Migrations;
    
    public partial class migration22 : DbMigration
    {
        public override void Up()
        {
            AlterColumn("dbo.RelatedArticles", "Url", c => c.String(maxLength: 500));
        }
        
        public override void Down()
        {
            AlterColumn("dbo.RelatedArticles", "Url", c => c.String(maxLength: 255));
        }
    }
}
