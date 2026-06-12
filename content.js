// ─────────────────────────────────────────────────────────────────
//  GAVIN STUDIO — Site Content Store (v2 — "From Pixels to Plans")
//  Edit via admin.html at http://localhost:3000/admin.html
// ─────────────────────────────────────────────────────────────────

const CONTENT_KEY = 'gavin_site_content_v2';

const DEFAULT_CONTENT = {

  // ── HERO ──────────────────────────────────────────────────────
  'hero-tag':          'Studio Final Project · 2025–26',
  'hero-line1':        'From',
  'hero-line2':        'Pixels',
  'hero-line3':        'to Plans',
  'hero-sub':          'An exploration of how technology and emerging digital tools are transforming the way buildings are designed, visualized, and brought to life.',
  'hero-student':      'Gavin Koch-Schulte',
  'hero-medium':       'Blender · 3D Print',
  'hero-discipline':   'Architectural Design',

  // ── ABOUT ─────────────────────────────────────────────────────
  'about-headline-1':  'A builder since',
  'about-headline-2':  'day one.',
  'about-p1':          'I feel like I have always been drawn to buildings and architecture. From Lego towers that almost touched the ceiling to massive blanket forts using every pillow and blanket in the house, I have always loved envisioning new ideas of how a place could look. As I got older my Lego creations moved into the Minecraft world, where I could build entire worlds using the same simple blocks and a never-ending imagination.',
  'about-p2':          'I loved going downtown with my Dad to see the massive old brick buildings that line the streets of Winnipeg\'s Exchange District, or seeing the different types of buildings we would find in different parts of the world on vacation. It was so neat to see that different areas of the world — just like different times in history — required and built different types of buildings.',
  'about-p3':          'Minecraft was, and still is, a really fun game that lets people of all ages and abilities create and explore amazing worlds. But as I got older I wanted to make buildings and environments that were more like the video games I was playing and the movies I was watching. So when I started to think about my Studio project, I knew it would have to involve architecture, 3D modeling, and cool buildings. The only problem: I didn\'t know anything about architecture or 3D modeling. Thankfully, it turns out those are exactly the sorts of problems that make a great studio project.',
  'about-p4':          'What started as a curiosity became a semester-long investigation into how technology is changing who gets to design buildings — and how well they can design them.',
  'stat-1-num':        '3',
  'stat-1-desc':       'Buildings Modelled',
  'stat-2-num':        '1',
  'stat-2-desc':       'Real Site Designed',
  'stat-3-num':        '1',
  'stat-3-desc':       'Architect Consulted',
  'stat-4-num':        '∞',
  'stat-4-desc':       'Hours in Blender',
  'about-caption':     '123 Bannatyne Ave, Winnipeg — the real building that inspired Gavin\'s most detailed model',

  // ── PROJECT ───────────────────────────────────────────────────
  'project-headline-1': 'Design buildings.',
  'project-headline-2': 'Think like',
  'project-headline-3': 'an architect.',
  'project-p1':         'My project began with a simple question: can I — a student with no formal training in architecture or 3D modeling — learn to design real buildings and models using the same software professionals use? The answer turned out to be: yes, with the right tools and a lot of guidance and effort.',
  'central-idea':       '"How new technology and emerging tools are making design more accessible to more people, and how that is impacting the overall design process."',

  'plan-heading':       'The plan sounded simple…',
  'plan-sub':           'Four steps from total beginner to designing an original building on a real Winnipeg development site.',
  'plan-1-title':       'Pick a software',
  'plan-1-body':        'Narrow the options down to Fusion, Blender, and SketchUp — then commit to one and go all in.',
  'plan-2-title':       'Learn the software',
  'plan-2-body':        'Use every available resource: online videos, tutorials, Blender user groups — anything that might help me understand and learn the program.',
  'plan-3-title':       'Recreate existing buildings',
  'plan-3-body':        'Practise, practise, practise. The Leaning Tower of Pisa, then 123 Bannatyne in the Exchange District — a building I was able to get into and walk around.',
  'plan-4-title':       'Design my own building',
  'plan-4-body':        'The final challenge: an original design using actual constraints from a real in-progress development site in Winnipeg, guided by AtLrg Architecture.',

  'goal-1-title':       'Master a professional 3D design tool',
  'goal-1-body':        'Learn Blender from scratch — the software big game studios use, film production houses, and increasingly, architecture firms.',
  'goal-2-title':       'Model real-world buildings',
  'goal-2-body':        'Recreate one famous landmark building along with a building local to Winnipeg to showcase the ability to capture detail and realism.',
  'goal-3-title':       'Attempt a completely original design for an actual site',
  'goal-3-body':        'Using real-life constraints and site conditions collected from discussions with AtLrg, a real Winnipeg architecture firm, develop a completely unique design that falls within the requirements and guidelines provided.',

  // ── JOURNEY ───────────────────────────────────────────────────
  'journey-headline-1': 'From',
  'journey-headline-2': 'Minecraft',
  'journey-headline-3': 'to the real thing.',
  'journey-intro':      'My path from Minecraft builder to Blender designer was a lot more difficult and frustrating than I had originally planned. Learning Blender took twice as long as I expected, and the amount of effort that goes into a single building was more as well. Thankfully, in the end I was able to grasp the important aspects and begin to develop the quality and style of buildings I could only dream of in Minecraft.',

  'tools-label':        'Choosing the tools',
  'tools-p1':           'Starting with the basics, I began to evaluate the various modeling tools available to me and laid out a plan to educate myself on how to use them. The various options all had their pros and cons — and they all seemed a lot more difficult than Roblox.',
  'tools-p2':           'Fusion was an ideal option because it is made by Autodesk, the industry leader behind AutoCAD — but it was difficult to get started because of their licensing process, and even with a student licence it ran very slowly on my computer. Blender was the other front runner, and to be honest I had always been interested in it because of its ability to do so much more than simply design a building. Once the building is done, you can keep creating beyond it — full city environments for video games and even movies. It seemed harder to learn, but I felt that because I was so excited about it I would enjoy the process a lot more… that was not exactly the case.',

  's1-label':   'Start',
  's1-title':   'It started with blocks',
  's1-p1':      'When I started using Minecraft I was so young, and everything computer-related was so new to me, that every little thing I created seemed amazing and wonderful. I think that made the gradual learning process a lot more enjoyable and natural.',
  's1-p2':      'Eventually the limitations of Minecraft and the tediousness of building in it pushed me to look for something better — but each time I tried, I found myself coming back. That is, until I found Roblox: another game that allowed users to create their own worlds, but it was very restrictive and also felt a bit childish.',
  's1-p3':      'It was great to be able to build cities and recreate famous locations and monuments, but they never looked quite real and always felt a bit off. What I liked most about Roblox was that while it let me create and design, it also gave me the ability to explore and share my creations.',
  's1-quote':   '"It was great to be able to build these cities and recreate famous landmarks and monuments, but for some reason they never felt quite real enough, and always seemed a little unfinished."',
  's1-cap1':    'Minecraft recreation — entire city blocks built from simple cubes',

  's2-label':   'Step 2',
  's2-title':   'Discovering Blender',
  's2-p1':      'After realizing that Fusion was not what I was ultimately looking for, I decided to jump into Blender 100%. It was a lot harder than I was expecting — and I was already expecting it to be hard. Thankfully there are literally thousands of hours of tutorials online that help you learn everything from downloading the application to getting your first item built. What made me choose Blender over Fusion and other design tools was that Blender was the only option that also had the ability to explore and expand on my creations.',
  's2-p2':      'I quickly realized that being able to build anything I could think of, in any way I wanted, came at the expense of nothing being easy. I don\'t know if it was because I was so used to Roblox and Minecraft, but I found it very hard to learn. This was the first real challenge that made me second-guess whether this should be my studio project.',
  's2-p3':      'Thankfully I found an online resource that personally walks you through tutorials — they can see exactly what I am doing, and what I am doing wrong, and help me over those initial difficult learning stages. It is another example of technology changing the way people learn, even in something as specific as Blender.',
  's2-cap1':    'First Blender project — the classic donut tutorial',
  's2-cap2':    'Guided crate tutorial — learning geometry, materials, and rendering',

  's3-label':   'Step 3',
  's3-title':   'The Leaning Tower of Pisa — and my second setback',
  's3-p1':      'The first building I made start-to-finish for the Studio project was the Leaning Tower of Pisa. It was a strategic choice — not only because of the endless reference images available online, but also because of its recurring shape for each level, which Blender handles well. It\'s also one of those buildings that almost anyone can guess within the first second of seeing it.',
  's3-p2':      'This is where the next significant challenge appeared. I had not realized how hard it was to add colour, texture, and lighting to objects inside Blender. Creating the geometry was already a challenge, but learning how to create detailed surfaces and textures — and how shadowing impacted them — was way more work than I had ever thought. For this reason, I decided to adjust my Studio goal: I would still focus on the shapes and materials of the buildings, but not focus too much on their colour or shadowing.',
  's3-cap1':    'Base colonnade — arch ring detail',
  's3-cap2':    'Upper levels — repeating geometry',

  's4-label':   'Step 4',
  's4-title':   '123 Bannatyne',
  's4-p1':      'I really wanted to get this one right. Having grown up loving to walk through the Exchange District with my family and look at all the cool old brick buildings — with their fire escapes and large brick archways — I felt I had a very good idea of what sort of details and approaches would be needed to capture everything.',
  's4-p2':      'This build took significantly longer than the Tower of Pisa and similar "practise builds," but I feel the results speak for themselves. The extra time and effort spent on the textures and the detailed window and column work were so effective that they even came through on the 3D-printed version — another example of new technology changing how design and architecture is approached. While 3D printing was not part of my initial Studio plan, it quickly proved itself a very useful and rewarding tool.',
  's4-cap1':    'The finished model — windows, cornices, and bump-outs matched to the real building',
  's4-cap2':    'Work in progress in Blender',
  's4-cap3':    'The real building, Exchange District',

  's5-label':   'Final',
  's5-title':   'Designing from scratch — with a real architect',
  's5-p1':      '3D printing became a very important part of my design process, and it was AtLrg that really showed me the true impact and power 3D printing has in communicating design ideas to people who may not be as experienced in design and rendering. Being able to quickly print an initial massing concept so someone can see it and physically hold it in their hand saves tons of wasted effort.',
  's5-p2':      'I learned this quickly after our initial meeting with Sean from AtLrg, when I was given our site constraints. I had initially designed a building to sit on the full site dimensions — only to learn there were significant utility and service lines underground on the south edge of the site that we could not build on. Having a physical 3D model to look at and move around helped in figuring out which portions of the building would have to be changed or deleted entirely. This process repeated itself with many of the constraints imposed on the site — whether a city requirement, an existing condition, or a client-imposed restriction.',
  'arch-heading': 'What the architect revealed',
  'arch-body':    'Real architectural design isn\'t just aesthetics — it\'s navigating an invisible network of constraints that determine where, how high, and how wide you can build. Each constraint changed the shape of the building.',
  'con-1':        'Driveway access requirements',
  'con-2':        'Underground service lines',
  'con-3':        'Sidewalk setbacks',
  'con-4':        'Parking minimums',
  'con-5':        'Building height limits',
  'con-6':        'City utility corridors',
  's5-cap1':      'City topographic map — underground utilities & site constraints',
  's5-cap2':      'Printed massing options in their real downtown context',

  // ── SHOWCASE ──────────────────────────────────────────────────
  'showcase-headline':  'Creative',
  'showcase-headline2': 'Accomplishments',
  'showcase-intro':     'From the first donut to a 3D-printed city model — a full view of what was built across the semester.',

  'item-1-tag':     'Final Project',
  'item-1-title':   '3D-Printed Winnipeg City Model',
  'item-1-caption': 'Physical massing studies for the exChange site, 3D printed in orange and placed in a full model of downtown Winnipeg',

  'item-2-tag':     'Heritage Building',
  'item-2-title':   '123 Bannatyne Ave',
  'item-2-caption': 'Precise Blender recreation of Winnipeg\'s heritage brick building',

  'item-3-tag':     'Reference',
  'item-3-title':   'The Real Building',
  'item-3-caption': 'The actual 123 Bannatyne Ave — matched window by window in 3D',

  'item-4-tag':     'Landmark',
  'item-4-title':   'Tower of Pisa',
  'item-4-caption': 'First major Blender build — base colonnade detail',

  'item-5-tag':     'Landmark',
  'item-5-title':   'Tower of Pisa',
  'item-5-caption': 'Upper colonnade ring — intricate arch repetition',

  'item-6-tag':     'Site Analysis',
  'item-6-title':   'exChange Site Topo',
  'item-6-caption': 'City topographic data used in the real design process',

  'capstone-tag':   'Capstone Achievement',
  'capstone-title': 'From Digital Model to Physical Reality',
  'capstone-p1':    'The culmination of the project wasn\'t just a Blender file — it was a physically 3D-printed massing model, placed on a full-scale 3D print of downtown Winnipeg. The orange models represent different design options for the exChange site, embedded in their real-world urban context.',
  'capstone-p2':    'This is the same process professional architecture firms use when presenting early design options to clients and city planners.',
  'capstone-li1':   'Multiple massing options designed and compared',
  'capstone-li2':   'Printed at 1:500 scale to match the city base model',
  'capstone-li3':   'Constraints from real city maps factored into every option',
  'capstone-li4':   'Presented in context of surrounding Winnipeg downtown',

  // ── FOOTER ────────────────────────────────────────────────────
  'footer-centre':  'Studio Final Project — 2025–26',
  'footer-name':    'Gavin Koch-Schulte',
  'footer-sub':     'Architecture & 3D Design',
};

// ── Public API ────────────────────────────────────────────────────────────────

function getContent() {
  try {
    const saved = localStorage.getItem(CONTENT_KEY);
    return saved ? Object.assign({}, DEFAULT_CONTENT, JSON.parse(saved)) : DEFAULT_CONTENT;
  } catch (e) {
    return DEFAULT_CONTENT;
  }
}

function saveContent(data) {
  localStorage.setItem(CONTENT_KEY, JSON.stringify(data));
}

function resetContent() {
  localStorage.removeItem(CONTENT_KEY);
}

// Apply content to the live page — call after DOM is ready
function applyContent() {
  const c = getContent();
  document.querySelectorAll('[data-c]').forEach(el => {
    const key = el.getAttribute('data-c');
    if (key in c) el.textContent = c[key];
  });
}
