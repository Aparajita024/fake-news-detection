import { ArrowLeft, AlertCircle, CheckCircle, Star } from "lucide-react";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Progress } from "./ui/progress";
import { useState } from "react";

interface HighlightedSegment {
  text: string;
  isSuspicious: boolean;
}

interface RelatedArticle {
  title: string;
  source: string;
  url: string;
}

interface AnalysisData {
  query: string;
  confidence: number;
  isFake: boolean;
  highlightedQuery?: HighlightedSegment[];
  explanation: {
    verdict: string;
    reasons?: string[];
  };
  relatedArticles?: RelatedArticle[];
}

interface ResultsSectionProps {
  data: AnalysisData;
  onReset: () => void;
}

export function ResultsSection({ data, onReset }: ResultsSectionProps) {
  const [rating, setRating] = useState(0);
  const [hoveredStar, setHoveredStar] = useState(0);

return (
  <div className="py-12 relative z-20">
    {/* Back Button */}
    <Button
      onClick={onReset}
      variant="ghost"
      className="mb-8 text-muted-foreground hover:text-foreground"
    >
      <ArrowLeft className="mr-2" size={18} />
      Check another
    </Button>


      {/* Results Container */}
      <div className="space-y-8">
        {/* Query Display with Highlights */}
        <Card className="bg-card/50 backdrop-blur-sm border-border p-6">
          <h2 className="text-xl mb-4 text-black">Analyzed Content</h2>
          <div className="text-lg leading-relaxed">
            {data.highlightedQuery && data.highlightedQuery.length > 0 ? (
              data.highlightedQuery.map((segment: any, index: number) => (
                <span
                  key={index}
                  className={
                    segment.isSuspicious
                      ? "bg-red-500/20 text-black px-1 rounded border-b-2 border-red-500/50"
                      : "text-foreground"
                  }
                >
                  {segment.text}
                </span>
              ))
            ) : (
              <span className="text-foreground">{data.query || 'No content available'}</span>
            )}
          </div>
        </Card>

        {/* Confidence Score */}
        <Card className="bg-card/50 backdrop-blur-sm border-border p-6">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-xl mb-2 text-black">Credibility Score</h2>
              <p className="text-sm text-black">
                Based on AI analysis of content patterns and sources
              </p>
            </div>
            <div className="flex flex-col items-center">
              <div className="relative w-24 h-24">
                <svg className="transform -rotate-90 w-24 h-24">
                  <circle
                    cx="48"
                    cy="48"
                    r="40"
                    stroke="currentColor"
                    strokeWidth="8"
                    fill="transparent"
                    className="text-border"
                  />
                  <circle
                    cx="48"
                    cy="48"
                    r="40"
                    stroke="Red"
                    strokeWidth="8"
                    fill="transparent"
                    strokeDasharray={`${2 * Math.PI * 40}`}
                    strokeDashoffset={`${2 * Math.PI * 40 * (1 - data.confidence / 100)}`}
                    className={
                      data.confidence >= 70
                        ? "text-green-500"
                        : data.confidence >= 40
                        ? "text-yellow-500"
                        : "text-red-500"
                    }
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-2xl">{data.confidence}%</span>
                </div>
              </div>
              <span className="mt-2 text-sm text-muted-foreground">Confidence</span>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Accuracy Assessment</span>
              <span
                className={
                  data.isFake
                    ? "text-red-400"
                    : "text-green-400"
                }
              >
                {data.isFake ? "Likely False" : "Likely True"}
              </span>
            </div>
            <Progress
              value={data.confidence}
              className="h-2"
            />
          </div>
        </Card>

        {/* Explanation Card */}
        <Card className="bg-card/50 backdrop-blur-sm border-border p-6">
          <div className="flex items-start gap-3 mb-4">
            {data.isFake ? (
              <AlertCircle className="text-red-500 flex-shrink-0 mt-1" size={24} />
            ) : (
              <CheckCircle className="text-green-500 flex-shrink-0 mt-1" size={24} />
            )}
            <div>
              <h2 className="text-xl mb-2 text-muted-foreground">Analysis Result</h2>
              <p className="text-lg mb-4">
                Verdict: <span className={data.isFake ? "text-red-400" : "text-green-400"}>{data.explanation.verdict}</span>
              </p>
            </div>
          </div>

          <div className="space-y-3 pl-9">
            <p className="text-muted-foreground text-sm mb-3">Key indicators:</p>
            {data.explanation?.reasons && data.explanation.reasons.length > 0 ? (
              data.explanation.reasons.map((reason: string, index: number) => (
                <div key={index} className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 flex-shrink-0" />
                  <p className="text-foreground">{reason}</p>
                </div>
              ))
            ) : (
              <p className="text-foreground italic">No additional analysis available</p>
            )}
          </div>
        </Card>

        {/* Related Articles */}
        <Card className="bg-card/50 backdrop-blur-sm border-border p-6">
          <h2 className="text-xl mb-4 text-muted-foreground">Related Articles</h2>
          <div className="space-y-3">
            {data.relatedArticles && data.relatedArticles.length > 0 ? (
              data.relatedArticles.map((article: any, index: number) => (
                <a
                  key={index}
                  href={article.url}
                  className="block p-4 bg-accent/30 hover:bg-accent/50 rounded-xl border border-border hover:border-ring transition-all group"
                >
                  <h3 className="text-foreground mb-2 group-hover:text-blue-400 transition-colors">
                    {article.title}
                  </h3>
                  <p className="text-sm text-muted-foreground">{article.source}</p>
                </a>
              ))
            ) : (
              <p className="text-foreground italic">No related articles available</p>
            )}
          </div>
        </Card>

        {/* Feedback Module */}
        <Card className="bg-card/50 backdrop-blur-sm border-border p-6">
          <div className="text-center">
            <h2 className="text-xl mb-4 text-muted-foreground">How useful was this result?</h2>
            <div className="flex justify-center gap-2 mb-4">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  onClick={() => setRating(star)}
                  onMouseEnter={() => setHoveredStar(star)}
                  onMouseLeave={() => setHoveredStar(0)}
                  className="transition-all transform hover:scale-110"
                >
                  <Star
                    size={32}
                    className={
                      star <= (hoveredStar || rating)
                        ? "fill-yellow-500 text-yellow-500"
                        : "text-muted-foreground"
                    }
                  />
                </button>
              ))}
            </div>
            {rating > 0 && (
              <p className="text-sm text-muted-foreground">
                Thank you for your feedback!
              </p>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
