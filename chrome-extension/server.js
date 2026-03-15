const express = require('express');
const path = require('path');

const app = express();
const PORT = 3002;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// In-memory listings store
let listings = [
  // Electronics
  {
    id: 1,
    title: 'MacBook Pro 14" M3',
    description:
      'Like-new MacBook Pro 14-inch with M3 chip, 16GB RAM, 512GB SSD. Includes original charger and box. Battery cycle count under 50. Perfect for developers and creatives.',
    price: 1450,
    category: 'Electronics',
    date: '2026-03-10',
    color: '#2563eb',
  },
  {
    id: 2,
    title: 'Sony WH-1000XM5 Headphones',
    description:
      'Industry-leading noise-canceling headphones in silver. Includes carrying case, USB-C cable, and airplane adapter. Excellent condition — upgraded to earbuds so these need a new home.',
    price: 215,
    category: 'Electronics',
    date: '2026-03-09',
    color: '#2563eb',
  },
  {
    id: 3,
    title: 'iPad Pro 12.9" (2022)',
    description:
      'M2 iPad Pro with 256GB storage, Space Gray. Wi-Fi only. Comes with Apple Pencil 2nd gen and Magic Keyboard folio. Screen protector applied from day one. No scratches.',
    price: 920,
    category: 'Electronics',
    date: '2026-03-07',
    color: '#2563eb',
  },
  {
    id: 4,
    title: 'Samsung 4K OLED Monitor 27"',
    description:
      '27-inch Samsung OLED gaming monitor, 144Hz, 1ms response time. Incredible color accuracy. Barely used — bought for a home office setup that changed. Includes original stand and cables.',
    price: 550,
    category: 'Electronics',
    date: '2026-03-05',
    color: '#2563eb',
  },
  {
    id: 5,
    title: 'Canon EOS R50 Mirrorless Camera',
    description:
      'Canon EOS R50 body with 18-45mm kit lens. Under 2,000 shutter actuations. Great for beginners and content creators. Comes with two batteries, charger, and original box.',
    price: 680,
    category: 'Electronics',
    date: '2026-03-02',
    color: '#2563eb',
  },
  {
    id: 6,
    title: 'Nintendo Switch OLED',
    description:
      'White Nintendo Switch OLED model in excellent condition. Comes with dock, Joy-Cons, and 6 game cartridges including Zelda: Tears of the Kingdom and Mario Kart 8 Deluxe.',
    price: 310,
    category: 'Electronics',
    date: '2026-02-28',
    color: '#2563eb',
  },
  {
    id: 7,
    title: 'Sonos Era 300 Speaker',
    description:
      'Sonos Era 300 in black, purchased 6 months ago. Spatial audio with Dolby Atmos support. Moving to a smaller apartment and can\'t take it with me. Original box included.',
    price: 330,
    category: 'Electronics',
    date: '2026-02-25',
    color: '#2563eb',
  },
  {
    id: 8,
    title: 'DJI Mini 4 Pro Drone',
    description:
      '4K/60fps drone with obstacle avoidance. Less than 5 hours of total flight time. Comes with Fly More combo: 3 batteries, carrying bag, and ND filter set. Registered with FAA.',
    price: 720,
    category: 'Electronics',
    date: '2026-02-20',
    color: '#2563eb',
  },
  // Furniture
  {
    id: 9,
    title: 'Mid-Century Modern Sofa',
    description:
      'Beautiful walnut-frame sofa with teal cushions. 84 inches wide. No stains, no pets, no smoking. Purchased from Article two years ago. Must pick up — will not deliver.',
    price: 625,
    category: 'Furniture',
    date: '2026-03-11',
    color: '#0d9488',
  },
  {
    id: 10,
    title: 'IKEA KALLAX 4x4 Shelf Unit',
    description:
      'White KALLAX shelf, 57"x57". Includes 8 drawer inserts. Great condition, minor scuff on one side not visible when placed against a wall. Disassembled and ready for pickup.',
    price: 95,
    category: 'Furniture',
    date: '2026-03-08',
    color: '#0d9488',
  },
  {
    id: 11,
    title: 'Solid Oak Dining Table + 6 Chairs',
    description:
      'Solid oak dining table, 72"x36", with 6 matching upholstered chairs. Light natural finish. One chair has a small stain on seat cushion, priced accordingly. Local pickup only.',
    price: 850,
    category: 'Furniture',
    date: '2026-03-06',
    color: '#0d9488',
  },
  {
    id: 12,
    title: 'Standing Desk (Flexispot E7)',
    description:
      'Flexispot E7 Pro electric standing desk, 60"x24" walnut top. Dual-motor, whisper-quiet, 355 lb capacity. Memory presets for 4 heights. Selling because I upgraded to a larger setup.',
    price: 480,
    category: 'Furniture',
    date: '2026-03-04',
    color: '#0d9488',
  },
  {
    id: 13,
    title: 'Herman Miller Aeron Chair (Size B)',
    description:
      'Classic Herman Miller Aeron in graphite, Size B (medium). Fully adjustable lumbar, armrests, and recline. Some normal wear on armrest pads but structurally perfect. Retail $1,400+.',
    price: 650,
    category: 'Furniture',
    date: '2026-03-01',
    color: '#0d9488',
  },
  {
    id: 14,
    title: 'Queen Platform Bed Frame — Walnut',
    description:
      'Low-profile walnut platform bed frame, queen size. No box spring needed. Slat system included. Minor assembly required. Purchased from West Elm 18 months ago. Excellent condition.',
    price: 390,
    category: 'Furniture',
    date: '2026-02-26',
    color: '#0d9488',
  },
  // Vehicles
  {
    id: 15,
    title: '2019 Honda Civic EX',
    description:
      'Well-maintained Civic with 42k miles. Clean title, single owner. Regularly serviced at the dealership. New tires last summer. Fuel efficient and reliable commuter car.',
    price: 18500,
    category: 'Vehicles',
    date: '2026-03-08',
    color: '#7c3aed',
  },
  {
    id: 16,
    title: '2021 Toyota RAV4 Hybrid',
    description:
      '2021 RAV4 Hybrid XSE in Magnetic Gray. 38k miles, one owner, clean Carfax. All-wheel drive, Apple CarPlay, heated seats, sunroof. Averaging 38 MPG combined. Ready for road trips.',
    price: 34900,
    category: 'Vehicles',
    date: '2026-03-06',
    color: '#7c3aed',
  },
  {
    id: 17,
    title: '2017 Harley-Davidson Street Glide',
    description:
      'Stage II Harley Street Glide Special with 28k miles. Milwaukee-Eight 107 engine, Screamin\' Eagle exhaust, Boom! Box infotainment. Always garaged, no accidents. Clear title.',
    price: 17500,
    category: 'Vehicles',
    date: '2026-03-03',
    color: '#7c3aed',
  },
  {
    id: 18,
    title: '2022 Tesla Model 3 Standard Range',
    description:
      'Midnight Silver Tesla Model 3 SR with 31k miles. Autopilot included, FSD transferable. Recently replaced tires and brake fluid. Home charging setup negotiable. Clean title.',
    price: 26800,
    category: 'Vehicles',
    date: '2026-02-27',
    color: '#7c3aed',
  },
  {
    id: 19,
    title: 'Trek FX3 Disc Hybrid Bike',
    description:
      '2023 Trek FX3 Disc, size Large, Matte Nautical Navy. Hydraulic disc brakes, carbon fork, 24-speed drivetrain. About 400 miles on it. Comes with rear rack and fenders already installed.',
    price: 680,
    category: 'Vehicles',
    date: '2026-02-22',
    color: '#7c3aed',
  },
  // Clothing
  {
    id: 20,
    title: 'Vintage Leather Jacket',
    description:
      'Genuine leather motorcycle jacket, size Medium. Broken-in but no damage — buttery soft. Classic moto style with asymmetric zip. A real head-turner.',
    price: 120,
    category: 'Clothing',
    date: '2026-03-12',
    color: '#c2410c',
  },
  {
    id: 21,
    title: 'Arc\'teryx Beta AR Jacket — Men\'s L',
    description:
      'Arc\'teryx Beta AR in Pilot (dark blue), men\'s Large. Gore-Tex Pro shell, used one full ski season. No repairs, all seams intact. Pit zips work perfectly. Retails for $750 new.',
    price: 390,
    category: 'Clothing',
    date: '2026-03-10',
    color: '#c2410c',
  },
  {
    id: 22,
    title: 'Lululemon Align Leggings Bundle (4 pairs)',
    description:
      'Four pairs of Lululemon Align leggings, size 6. Colors: black (x2), dark olive, heathered navy. All in excellent condition, washed per instructions, no pilling. Selling as a bundle only.',
    price: 175,
    category: 'Clothing',
    date: '2026-03-07',
    color: '#c2410c',
  },
  {
    id: 23,
    title: 'Red Wing Iron Ranger Boots — Size 10.5',
    description:
      'Red Wing Iron Ranger in Amber Harness leather, size 10.5 D. Worn about 20 times. Already broken in and resoleable. Includes original box and extra laces. These last a lifetime.',
    price: 195,
    category: 'Clothing',
    date: '2026-03-04',
    color: '#c2410c',
  },
  {
    id: 24,
    title: 'Patagonia Down Sweater Hoody — Women\'s M',
    description:
      'Patagonia Down Sweater Hoody in Crater Blue, women\'s Medium. 800-fill-power down, DWR finish still active. Minor pilling on cuffs. Warm, packable, and versatile. Great for travel.',
    price: 85,
    category: 'Clothing',
    date: '2026-03-01',
    color: '#c2410c',
  },
  // Services
  {
    id: 25,
    title: 'Professional Dog Walking',
    description:
      'Experienced and insured dog walker offering daily walks in the downtown area. 30-minute or 1-hour sessions available. Flexible scheduling, great references. Your pup will love it.',
    price: 25,
    category: 'Services',
    date: '2026-03-13',
    color: '#16a34a',
  },
  {
    id: 26,
    title: 'Home Deep Cleaning Service',
    description:
      'Professional deep cleaning for apartments and houses up to 2,000 sq ft. Includes inside oven, fridge, baseboards, and windows. Eco-friendly products. 5-star rated on Nextdoor.',
    price: 180,
    category: 'Services',
    date: '2026-03-11',
    color: '#16a34a',
  },
  {
    id: 27,
    title: 'Freelance Web Development',
    description:
      'Full-stack developer with 8 years of experience. React, Node.js, and Postgres. Available for new projects or ongoing retainer work. Portfolio available on request. Remote-friendly.',
    price: 95,
    category: 'Services',
    date: '2026-03-09',
    color: '#16a34a',
  },
  {
    id: 28,
    title: 'Personal Chef — Dinner Parties',
    description:
      'Private chef with 12 years of restaurant experience. Specializing in Mediterranean and farm-to-table cuisine. Will shop, cook, and clean up. Ideal for dinner parties of 4–12 guests.',
    price: 250,
    category: 'Services',
    date: '2026-03-06',
    color: '#16a34a',
  },
  {
    id: 29,
    title: 'Piano Lessons — All Ages & Levels',
    description:
      'Conservatory-trained pianist offering in-home lessons in the metro area. Beginners through advanced students welcome. 30 or 60-minute slots available weekday evenings and weekends.',
    price: 65,
    category: 'Services',
    date: '2026-03-03',
    color: '#16a34a',
  },
  {
    id: 30,
    title: 'Photography — Portraits & Events',
    description:
      'Professional photographer available for headshots, family portraits, and small events. Edited gallery delivered within one week. 2-hour minimum. Travel within 30 miles of downtown.',
    price: 200,
    category: 'Services',
    date: '2026-02-28',
    color: '#16a34a',
  },
];

let nextId = 31;

// GET all listings
app.get('/api/listings', (req, res) => {
  res.json(listings);
});

// GET a single listing by ID
app.get('/api/listings/:id', (req, res) => {
  const listing = listings.find((l) => l.id === parseInt(req.params.id));
  if (!listing) {
    return res.status(404).json({ error: 'Listing not found' });
  }
  res.json(listing);
});

// POST a new listing
app.post('/api/listings', (req, res) => {
  const { title, description, price, category } = req.body;

  if (!title || !price || !category) {
    return res.status(400).json({ error: 'Title, price, and category are required' });
  }

  const categoryColors = {
    Electronics: '#2563eb',
    Furniture: '#0d9488',
    Vehicles: '#7c3aed',
    Clothing: '#c2410c',
    Services: '#16a34a',
  };

  const listing = {
    id: nextId++,
    title,
    description: description || '',
    price: parseFloat(price),
    category,
    date: new Date().toISOString().split('T')[0],
    color: categoryColors[category] || '#6b7280',
  };

  listings.push(listing);
  res.status(201).json(listing);
});

app.listen(PORT, () => {
  console.log(`Marketplace server running at http://localhost:${PORT}`);
});
