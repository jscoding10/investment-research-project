import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SimpleMarkdownComponent } from './simple-markdown.component';

describe('SimpleMarkdownComponent', () => {
  let component: SimpleMarkdownComponent;
  let fixture: ComponentFixture<SimpleMarkdownComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SimpleMarkdownComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SimpleMarkdownComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
