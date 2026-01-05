export const PRESET_DATA: Record<string, any> = {
  "What is the capital of Brazil?": {
    question: "What is the capital of Brazil?",
    groundTruth: "Brasília",
    hints: [
      { hint_text: "It is a planned city founded in 1960.", hint_id: 1 },
      { hint_text: "It is located in the Federal District.", hint_id: 2 },
      { hint_text: "It was designed by Oscar Niemeyer and Lúcio Costa.", hint_id: 3 },
      { hint_text: "It replaced Rio de Janeiro as the capital.", hint_id: 4 }
    ],
    candidates: [
      "Rio de Janeiro", "São Paulo", "Salvador", "Belo Horizonte", "Curitiba", "Brasília"
    ],
    // Pre-computed metrics
    metricsById: {},
    eliminationMap: {}
  },

  "Which planet is known as the Red Planet?": {
    question: "Which planet is known as the Red Planet?",
    groundTruth: "Mars",
    hints: [
      { hint_text: "It is the fourth planet from the Sun.", hint_id: 5 },
      { hint_text: "It has two small moons named Phobos and Deimos.", hint_id: 6 },
      { hint_text: "Its surface is rich in iron oxide, giving it a rusty color.", hint_id: 7 },
      { hint_text: "It is named after the Roman god of war.", hint_id: 8 }
    ],
    candidates: [
      "Venus", "Jupiter", "Saturn", "Mercury", "Neptune", "Mars"
    ],
    metricsById: {}, 
    eliminationMap: {}
  },

  "Who wrote The Hobbit?": {
    question: "Who wrote The Hobbit?",
    groundTruth: "J.R.R. Tolkien",
    hints: [
      { hint_text: "He was a professor of Anglo-Saxon at Oxford University.", hint_id: 9 },
      { hint_text: "He also wrote The Lord of the Rings trilogy.", hint_id: 10 },
      { hint_text: "He is often considered the father of modern high fantasy literature.", hint_id: 11 },
      { hint_text: "His initials are J.R.R.", hint_id: 12 }
    ],
    candidates: [
      "J.K. Rowling", "C.S. Lewis", "George R.R. Martin", "Roald Dahl", "Isaac Asimov", "J.R.R. Tolkien"
    ],
    metricsById: {},
    eliminationMap: {}
  },

  "What is the tallest mountain in the world?": {
    question: "What is the tallest mountain in the world?",
    groundTruth: "Mount Everest",
    hints: [
      { hint_text: "It is located in the Mahalangur Himal sub-range of the Himalayas.", hint_id: 13 },
      { hint_text: "It sits on the border between Nepal and China.", hint_id: 14 },
      { hint_text: "Its peak is 8,848 meters (29,029 ft) above sea level.", hint_id: 15 },
      { hint_text: "It is named after a British Surveyor General of India.", hint_id: 16 }
    ],
    candidates: [
      "K2", "Mount Kilimanjaro", "Denali", "Mount Fuji", "Mont Blanc", "Mount Everest"
    ],
    metricsById: {},
    eliminationMap: {}
  },

  "Who discovered penicillin?": {
    question: "Who discovered penicillin?",
    groundTruth: "Alexander Fleming",
    hints: [
      { hint_text: "He was a Scottish physician and microbiologist.", hint_id: 17 },
      { hint_text: "The discovery happened accidentally in 1928 at St Mary's Hospital, London.", hint_id: 18 },
      { hint_text: "He noticed that a mold called Penicillium notatum killed bacteria in a petri dish.", hint_id: 19 },
      { hint_text: "He shared the Nobel Prize in Physiology or Medicine in 1945.", hint_id: 20 }
    ],
    candidates: [
      "Marie Curie", "Louis Pasteur", "Charles Darwin", "Albert Einstein", "Isaac Newton", "Alexander Fleming"
    ],
    metricsById: {},
    eliminationMap: {}
  },

  "What is the largest ocean on Earth?": {
    question: "What is the largest ocean on Earth?",
    groundTruth: "Pacific Ocean",
    hints: [
      { hint_text: "It covers more than 30% of Earth's surface.", hint_id: 21 },
      { hint_text: "Its name was coined by explorer Ferdinand Magellan, meaning 'peaceful'.", hint_id: 22 },
      { hint_text: "It contains the Mariana Trench, the deepest part of the world's oceans.", hint_id: 23 },
      { hint_text: "It separates Asia and Australia from the Americas.", hint_id: 24 }
    ],
    candidates: [
      "Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Southern Ocean", "Mediterranean Sea", "Pacific Ocean"
    ],
    metricsById: {},
    eliminationMap: {}
  }
};