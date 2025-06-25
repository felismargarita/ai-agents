import { Component, inject } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { MarkdownModule } from 'ngx-markdown';

@Component({
  selector: 'app-meeting',
  imports: [ReactiveFormsModule, MarkdownModule],
  templateUrl: './meeting.html',
  styleUrl: './meeting.scss'
})
export class Meeting {
  private httpClient = inject(HttpClient);
  public processing = false
  public success = false

  public meetingContent = new FormControl('')
  public markdownText: string | null = ''

  submit() {
    if (!this.meetingContent.value) return
    this.processing = true
    this.success = false
    this.httpClient.post(
      'http://localhost:8000/meeting_markdown',
      { content: this.meetingContent.value }
    ).subscribe(config => {
      this.markdownText = config as string
      this.processing = false
      this.success = true
    })
  }

}
