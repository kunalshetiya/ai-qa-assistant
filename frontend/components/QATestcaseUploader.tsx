"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Toaster, toast } from "react-hot-toast";

export default function QATestcaseUploader() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [loading, setLoading] = useState(false);
  const [output, setOutput] = useState("");
  const [downloadUrl, setDownloadUrl] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    setFiles(e.target.files);
  };

  const handleSubmit = async () => {
    if (!files || files.length === 0) {
      toast.error("Please upload a requirement document.");
      return;
    }

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append("file", files[i]);
    }

    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:5000/generate-testcases", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (res.ok && data?.download_url) {
        setDownloadUrl("http://127.0.0.1:5000/download");
        setOutput("Test cases generated successfully.");
        toast.success("Test cases generated!");
      } else {
        toast.error(data?.error || "Failed to generate test cases.");
      }
    } catch (err) {
      console.error("Error:", err);
      toast.error("Failed to connect to backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto py-12 px-4 text-gray-900 dark:text-white bg-white dark:bg-black min-h-screen">
      <Toaster position="top-right" />

      {/* 🔥 NEW TITLE */}
      <h1 className="text-3xl font-bold mb-2 text-center">
        AI QA Assistant
      </h1>

      <p className="text-center mb-6 text-gray-500">
        Generate test cases and edge cases using AI
      </p>

      <Card className="dark:bg-zinc-900">
        <CardContent className="space-y-4 p-6">
          <div className="space-y-2">
            <Label htmlFor="file">
              Upload Requirement Document (PDF/DOCX)
            </Label>
            <Input id="file" type="file" multiple onChange={handleFileChange} />
          </div>

          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? "Generating..." : "Generate Test Cases"}
          </Button>

          {/* 🔥 DOWNLOAD BUTTON */}
          {downloadUrl && (
            <a href={downloadUrl} download>
              <Button variant="outline" className="mt-2">
                Download Excel
              </Button>
            </a>
          )}
        </CardContent>
      </Card>

      {/* 🔥 OUTPUT DISPLAY */}
      {output && (
        <div className="mt-8 bg-gray-100 dark:bg-zinc-800 p-4 rounded text-sm whitespace-pre-wrap">
          <strong className="block mb-2">Output:</strong>
          {output}
        </div>
      )}

      {/* 🔥 FOOTER (PRO TOUCH) */}
      <p className="text-center text-xs mt-6 text-gray-400">
        AI-powered QA automation tool
      </p>
    </div>
  );
}