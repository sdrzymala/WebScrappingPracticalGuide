namespace WebScrapingPudelekPL.Migrations
{
    using System;
    using System.Data.Entity.Migrations;
    
    public partial class update17 : DbMigration
    {
        public override void Up()
        {
            CreateTable(
                "dbo.RelatedArticles",
                c => new
                    {
                        Id = c.Int(nullable: false, identity: true),
                        RelatedText = c.String(maxLength: 255),
                        RelatedName = c.String(maxLength: 255),
                        Article_Id = c.Int(),
                    })
                .PrimaryKey(t => t.Id)
                .ForeignKey("dbo.Articles", t => t.Article_Id)
                .Index(t => t.Article_Id);
            
        }
        
        public override void Down()
        {
            DropForeignKey("dbo.RelatedArticles", "Article_Id", "dbo.Articles");
            DropIndex("dbo.RelatedArticles", new[] { "Article_Id" });
            DropTable("dbo.RelatedArticles");
        }
    }
}
