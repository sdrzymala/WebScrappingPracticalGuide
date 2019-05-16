using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.ComponentModel;

namespace WebScrapingPudelekPL.Classes
{
    public class Article
    {
        [Key]
        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
        public int article_id { get; set; }

        [StringLength(255)]
        public string article_url { get; set; }

        [StringLength(255)]
        public string article_type { get; set; }

        [StringLength(500)]
        public string article_title { get; set; }

        public DateTime? article_created_at { get; set; }

        [StringLength(255)]
        public string article_author { get; set; }

        [MaxLength]
        public string article_content { get; set; }

        public int? article_number_of_comments { get; set; }

        public int? article_number_of_bolded_text { get; set; }

        public bool? article_has_slideshow { get; set; }

        public bool? article_has_video { get; set; }

        public int? article_number_of_images { get; set; }

        public int? article_number_of_likes { get; set; }

        public bool? article_is_downloaded { get; set; }

        public DateTime? article_inserted_at { get; set; }

        public DateTime? article_updated_at { get; set; }

        public virtual List<Comment> Comments { get; set; }

        public virtual List<Tag> Tags { get; set; }

        public virtual List<RelatedArticle> RelatedArticles { get; set; }

    }
}
