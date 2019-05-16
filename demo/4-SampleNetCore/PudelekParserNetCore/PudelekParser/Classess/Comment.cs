using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.ComponentModel;

namespace WebScrapingPudelekPL.Classes
{
    public class Comment
    {
        [Key]
        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
        public int comment_id { get; set; }

        public int? article_id { get; set; }

        [StringLength(255)]
        public string comment_author { get; set; }

        public DateTime? comment_created_at { get; set; }

        [MaxLength]
        public string comment_message { get; set; }

        public int? comment_thumbs_up { get; set; }

        public int? comment_thumbs_down { get; set; }

        public bool? comment_is_highlited { get; set; }

    }
}
