using System;
using System.Collections.Generic;
using System.Text;
using System.Text.RegularExpressions;

namespace PudelekParser
{
    public class HelperMethods
    {
        public static string CleanText(string str)
        {
            return RemoveMultipleSpaces(RemoveSpecialCharacters(str)).Trim().ToLower();
        }

        public static string RemoveSpecialCharacters(string str)
        {
            StringBuilder sb = new StringBuilder();

            for (int i = 0; i < str.Length; i++)
            {
                if (char.IsLetterOrDigit(str[i]) || str[i] == ' ')
                {
                    sb.Append(str[i]);
                }
                else
                {
                    sb.Append(' ');
                }
            }

            return sb.ToString();
        }

        public static string RemoveMultipleSpaces(string str)
        {
            return Regex.Replace(str, @"\s+", " ");
        }

    }
}
